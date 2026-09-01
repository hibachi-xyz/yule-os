"""Byte-level regression tests for signature payload encoding.

The existing withdraw/transfer tests assert only on the decoded response object
(``response.orderId`` / ``response.status``), so nothing in the suite ever
inspected the bytes that are actually hashed and signed. That gap is why the
float-based fixed-point conversion and the unvalidated hex address decoding
below went unnoticed: both produce a well-formed request that the server
rejects, or worse, a signature over a different message than the one submitted.

Every test here asserts on exact bytes rather than on a round-tripped value.
"""

from decimal import Decimal

import pytest

from hibachi_xyz.api import (
    EVM_ADDRESS_BYTE_LENGTH,
    FEE_PERCENT_SCALE,
    SETTLEMENT_SCALE,
    _hex_to_bytes,
    _query_value,
    _scaled_amount_to_bytes,
    _side_to_bytes,
    _strip_hex_prefix,
)
from hibachi_xyz.errors import ValidationError
from hibachi_xyz.types import Side


class TestScaledAmountToBytes:
    """Fixed-point encoding of settlement amounts and fee percentages."""

    def test_whole_number_settlement_amount(self):
        result = _scaled_amount_to_bytes("100.0", SETTLEMENT_SCALE, 8, "quantity")
        assert result == (100_000_000).to_bytes(8, "big")

    def test_fractional_settlement_amount(self):
        result = _scaled_amount_to_bytes("1.5", SETTLEMENT_SCALE, 8, "quantity")
        assert result == (1_500_000).to_bytes(8, "big")

    def test_float_precision_loss_no_longer_leaks_into_signature(self):
        """``float("2.01") * 1e6`` is 2009999.9999999998, so the previous
        ``int(float(...) * 1e6)`` encoded 2_009_999 - one unit below the
        full-precision amount transmitted in the request body.
        """
        assert int(float("2.01") * 1e6) == 2_009_999  # the defect, for the record

        result = _scaled_amount_to_bytes("2.01", SETTLEMENT_SCALE, 8, "quantity")
        assert result == (2_010_000).to_bytes(8, "big")

    def test_full_six_decimal_precision_is_preserved(self):
        result = _scaled_amount_to_bytes("0.000001", SETTLEMENT_SCALE, 8, "quantity")
        assert result == (1).to_bytes(8, "big")

    def test_decimal_input(self):
        result = _scaled_amount_to_bytes(
            Decimal("2.750000"), SETTLEMENT_SCALE, 8, "quantity"
        )
        assert result == (2_750_000).to_bytes(8, "big")

    def test_zero_is_allowed(self):
        result = _scaled_amount_to_bytes("0", SETTLEMENT_SCALE, 8, "quantity")
        assert result == (0).to_bytes(8, "big")

    def test_excess_precision_is_rejected_not_truncated(self):
        """Silently truncating would sign an amount other than the one sent."""
        with pytest.raises(ValidationError, match="more precision"):
            _scaled_amount_to_bytes("1.0000001", SETTLEMENT_SCALE, 8, "quantity")

    def test_negative_amount_is_rejected(self):
        with pytest.raises(ValidationError, match="must not be negative"):
            _scaled_amount_to_bytes("-1", SETTLEMENT_SCALE, 8, "quantity")

    def test_overflow_is_rejected(self):
        with pytest.raises(ValidationError):
            _scaled_amount_to_bytes("1e30", SETTLEMENT_SCALE, 8, "quantity")

    def test_fee_percent_scale(self):
        result = _scaled_amount_to_bytes(
            "0.00045", FEE_PERCENT_SCALE, 8, "maxFeesPercent"
        )
        assert result == (45_000).to_bytes(8, "big")

    def test_field_name_appears_in_error(self):
        with pytest.raises(ValidationError, match="Withdrawal maxFees"):
            _scaled_amount_to_bytes(
                "0.00000001", SETTLEMENT_SCALE, 8, "Withdrawal maxFees"
            )


class TestHexToBytes:
    """Hex decoding for address and public-key digest fields."""

    def test_valid_evm_address_with_prefix(self):
        address = "0x" + "ab" * EVM_ADDRESS_BYTE_LENGTH
        assert _hex_to_bytes(
            address, "Withdrawal address", EVM_ADDRESS_BYTE_LENGTH
        ) == bytes([0xAB]) * EVM_ADDRESS_BYTE_LENGTH

    def test_valid_evm_address_without_prefix(self):
        address = "cd" * EVM_ADDRESS_BYTE_LENGTH
        assert _hex_to_bytes(
            address, "Withdrawal address", EVM_ADDRESS_BYTE_LENGTH
        ) == bytes([0xCD]) * EVM_ADDRESS_BYTE_LENGTH

    def test_surrounding_whitespace_is_tolerated(self):
        address = "  0x" + "01" * EVM_ADDRESS_BYTE_LENGTH + "  "
        assert (
            len(_hex_to_bytes(address, "Withdrawal address", EVM_ADDRESS_BYTE_LENGTH))
            == EVM_ADDRESS_BYTE_LENGTH
        )

    def test_short_address_is_rejected(self):
        """A short address used to decode cleanly and shift every later digest
        field, so the signature covered a different message.
        """
        with pytest.raises(ValidationError, match="must be 20 bytes"):
            _hex_to_bytes("0x1234", "Withdrawal address", EVM_ADDRESS_BYTE_LENGTH)

    def test_long_address_is_rejected(self):
        with pytest.raises(ValidationError, match="must be 20 bytes"):
            _hex_to_bytes(
                "0x" + "ab" * 21, "Withdrawal address", EVM_ADDRESS_BYTE_LENGTH
            )

    def test_odd_length_is_rejected(self):
        with pytest.raises(ValidationError, match="not a valid hex string"):
            _hex_to_bytes("0xabc", "Withdrawal address", None)

    def test_non_hex_characters_are_rejected(self):
        with pytest.raises(ValidationError, match="not a valid hex string"):
            _hex_to_bytes("0x" + "zz" * 20, "Withdrawal address", None)

    def test_empty_value_is_rejected(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            _hex_to_bytes("0x", "Transfer destination public key", None)

    def test_unconstrained_length_is_accepted(self):
        """Transfer destination public keys are not EVM addresses, so only the
        hex encoding itself is validated for them.
        """
        assert _hex_to_bytes("0x" + "ff" * 32, "public key", None) == b"\xff" * 32


class TestStripHexPrefix:
    """Prefix stripping must not remove ``0x`` from the middle of a value."""

    def test_strips_lowercase_prefix(self):
        assert _strip_hex_prefix("0xdeadbeef") == "deadbeef"

    def test_strips_uppercase_prefix(self):
        assert _strip_hex_prefix("0Xdeadbeef") == "deadbeef"

    def test_leaves_unprefixed_value_untouched(self):
        assert _strip_hex_prefix("deadbeef") == "deadbeef"

    def test_does_not_strip_interior_occurrences(self):
        """``"a0x0b".replace("0x", "")`` yields ``"a0b"`` - a different, shorter
        value that still decodes as hex.
        """
        assert _strip_hex_prefix("ab0xcd") == "ab0xcd"

    def test_empty_string(self):
        assert _strip_hex_prefix("") == ""


class TestSideToBytes:
    """Order side encoding, including the BUY/SELL aliases."""

    def test_ask_encodes_as_zero(self):
        assert _side_to_bytes(Side.ASK) == (0).to_bytes(4, "big")

    def test_sell_encodes_as_zero(self):
        """``Side.SELL`` previously fell through the ``side.value == "ASK"``
        check and was signed as 1 (BID) - the opposite side.
        """
        assert _side_to_bytes(Side.SELL) == (0).to_bytes(4, "big")

    def test_bid_encodes_as_one(self):
        assert _side_to_bytes(Side.BID) == (1).to_bytes(4, "big")

    def test_buy_encodes_as_one(self):
        assert _side_to_bytes(Side.BUY) == (1).to_bytes(4, "big")

    def test_aliases_agree_with_canonical_sides(self):
        assert _side_to_bytes(Side.SELL) == _side_to_bytes(Side.ASK)
        assert _side_to_bytes(Side.BUY) == _side_to_bytes(Side.BID)

    def test_unknown_side_is_rejected(self):
        with pytest.raises(ValidationError, match="Unsupported order side"):
            _side_to_bytes("LONG")  # type: ignore[arg-type]


class TestQueryValue:
    """Percent-encoding of values interpolated into request query strings."""

    def test_symbol_slash_is_preserved(self):
        """Existing symbols must be transmitted byte-for-byte as before."""
        assert _query_value("BTC/USDT-P") == "BTC/USDT-P"

    def test_plain_values_are_unchanged(self):
        assert _query_value("ETH-USDT") == "ETH-USDT"
        assert _query_value(12345) == "12345"

    def test_ampersand_is_encoded(self):
        assert _query_value("BTC/USDT-P&accountId=999") == (
            "BTC/USDT-P%26accountId%3D999"
        )

    def test_question_mark_and_hash_are_encoded(self):
        assert _query_value("a?b#c") == "a%3Fb%23c"

    def test_whitespace_is_encoded(self):
        assert _query_value("a b") == "a%20b"
