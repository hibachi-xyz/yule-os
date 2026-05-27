"""Tests for TPSLConfig._as_requests."""

from decimal import Decimal

from hibachi_xyz.types import Side, TPSLConfig, TriggerDirection


class TestTPSLConfigAsRequests:
    def _make_requests(self, tpsl, parent_side):
        return tpsl._as_requests(
            parent_symbol="BTC/USDT-P",
            parent_quantity="0.001",
            parent_side=parent_side,
            parent_nonce=12345,
            max_fees_percent="0.001",
        )

    def test_take_profit_trigger_price_matches_leg_price(self):
        tpsl = TPSLConfig().add_take_profit(price=70000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_price == Decimal("70000")

    def test_stop_loss_trigger_price_matches_leg_price(self):
        tpsl = TPSLConfig().add_stop_loss(price=40000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_price == Decimal("40000")

    def test_trigger_price_is_not_max_fees_percent(self):
        tpsl = TPSLConfig().add_take_profit(price=70000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_price != orders[0].max_fees_percent

    def test_ask_take_profit_trigger_price_matches_leg_price(self):
        tpsl = TPSLConfig().add_take_profit(price=40000)
        orders = self._make_requests(tpsl, Side.ASK)
        assert orders[0].trigger_price == Decimal("40000")

    def test_ask_stop_loss_trigger_price_matches_leg_price(self):
        tpsl = TPSLConfig().add_stop_loss(price=70000)
        orders = self._make_requests(tpsl, Side.ASK)
        assert orders[0].trigger_price == Decimal("70000")

    def test_multiple_legs_each_get_correct_trigger_price(self):
        tpsl = TPSLConfig().add_take_profit(price=70000).add_stop_loss(price=40000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_price == Decimal("70000")
        assert orders[1].trigger_price == Decimal("40000")

    def test_ask_multiple_legs_each_get_correct_trigger_price(self):
        tpsl = TPSLConfig().add_take_profit(price=40000).add_stop_loss(price=70000)
        orders = self._make_requests(tpsl, Side.ASK)
        assert orders[0].trigger_price == Decimal("40000")
        assert orders[1].trigger_price == Decimal("70000")

    def test_bid_parent_tp_uses_high_direction(self):
        tpsl = TPSLConfig().add_take_profit(price=70000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_direction == TriggerDirection.HIGH

    def test_bid_parent_sl_uses_low_direction(self):
        tpsl = TPSLConfig().add_stop_loss(price=40000)
        orders = self._make_requests(tpsl, Side.BID)
        assert orders[0].trigger_direction == TriggerDirection.LOW

    def test_ask_parent_tp_uses_low_direction(self):
        tpsl = TPSLConfig().add_take_profit(price=40000)
        orders = self._make_requests(tpsl, Side.ASK)
        assert orders[0].trigger_direction == TriggerDirection.LOW

    def test_ask_parent_sl_uses_high_direction(self):
        tpsl = TPSLConfig().add_stop_loss(price=70000)
        orders = self._make_requests(tpsl, Side.ASK)
        assert orders[0].trigger_direction == TriggerDirection.HIGH
