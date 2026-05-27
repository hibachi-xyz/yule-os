import pytest

from hibachi_xyz.errors import ValidationError
from hibachi_xyz.executors.interface import HttpResponse
from hibachi_xyz.types import (
    FutureContract,
    Side,
    TPSLConfig,
    TriggerDirection,
    TWAPConfig,
    TWAPQuantityMode,
)
from tests.mock_executors import MockSuccessfulOutput
from tests.unit.conftest import load_json_all_cases


@pytest.mark.parametrize("test_data", load_json_all_cases("test.place_market_order"))
def test_place_market_order(mock_http_client, test_data):
    payload, path = test_data
    client, mock_http = mock_http_client

    # Extract payloads
    exchange_info = payload["response.exchange_info"]
    order_response = payload["response.order"]

    # Extract test parameters from order response
    symbol = order_response["symbol"]
    quantity = order_response["quantity"]
    side = Side(order_response["side"])
    max_fees_percent = order_response["maxFeesPercent"]

    # Mock exchange_info call (needed for __get_contract in place_market_order)
    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=exchange_info),
            call_validation=lambda call: call.function_name == "send_simple_request"
            and call.arg_pack == ("/market/exchange-info",),
        )
    )

    # Mock send_authorized_request call for order placement
    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=order_response),
            call_validation=lambda call: call.function_name == "send_authorized_request"
            and call.arg_pack[0:2] == ("POST", "/trade/order")
            and call.arg_pack[2] is not None,
        )
    )

    nonce, order_id = client.place_market_order(
        symbol, quantity, side, max_fees_percent
    )

    # Assertions
    assert order_id == order_response["orderId"]


def test_place_market_order_twap_with_trigger_price(mock_http_client):
    """Test that placing market order with both twap_config and trigger_price raises ValidationError."""
    client, mock_http = mock_http_client

    symbol = "BTC/USDT-P"
    client._future_contracts = {
        symbol: FutureContract(
            displayName="BTC/USDT Perps",
            id=1,
            initialMarginRate="0.066667",
            maintenanceMarginRate="0.046667",
            marketCloseTimestamp=None,
            marketCreationTimestamp="1727701319.73488",
            marketOpenTimestamp=None,
            minNotional="1",
            minOrderSize="0.000000001",
            orderbookGranularities=["0.01", "0.1", "1"],
            settlementDecimals=6,
            settlementSymbol="USDT",
            status="LIVE",
            stepSize="0.000000001",
            symbol=symbol,
            tickSize="0.000001",
            underlyingDecimals=8,
            underlyingSymbol="BTC",
        )
    }

    twap_config = TWAPConfig(duration_minutes=5, quantity_mode=TWAPQuantityMode.FIXED)

    with pytest.raises(ValidationError) as exc_info:
        client.place_market_order(
            symbol=symbol,
            quantity=0.001,
            side=Side.BUY,
            max_fees_percent=0.001,
            trigger_price=50000,
            twap_config=twap_config,
        )

    assert "Can not set trigger price for TWAP order" in str(exc_info.value)


def test_place_market_order_twap_with_tpsl(mock_http_client):
    """Test that placing market order with both twap_config and tpsl raises ValidationError."""
    client, mock_http = mock_http_client

    symbol = "BTC/USDT-P"
    client._future_contracts = {
        symbol: FutureContract(
            displayName="BTC/USDT Perps",
            id=1,
            initialMarginRate="0.066667",
            maintenanceMarginRate="0.046667",
            marketCloseTimestamp=None,
            marketCreationTimestamp="1727701319.73488",
            marketOpenTimestamp=None,
            minNotional="1",
            minOrderSize="0.000000001",
            orderbookGranularities=["0.01", "0.1", "1"],
            settlementDecimals=6,
            settlementSymbol="USDT",
            status="LIVE",
            stepSize="0.000000001",
            symbol=symbol,
            tickSize="0.000001",
            underlyingDecimals=8,
            underlyingSymbol="BTC",
        )
    }

    twap_config = TWAPConfig(duration_minutes=5, quantity_mode=TWAPQuantityMode.FIXED)
    tpsl_config = TPSLConfig()

    with pytest.raises(ValidationError) as exc_info:
        client.place_market_order(
            symbol=symbol,
            quantity=0.001,
            side=Side.BUY,
            max_fees_percent=0.001,
            twap_config=twap_config,
            tpsl=tpsl_config,
        )

    assert "Can not set tpsl for TWAP order" in str(exc_info.value)


BTC_CONTRACT = FutureContract(
    displayName="BTC/USDT Perps",
    id=1,
    initialMarginRate="0.066667",
    maintenanceMarginRate="0.046667",
    marketCloseTimestamp=None,
    marketCreationTimestamp="1727701319.73488",
    marketOpenTimestamp=None,
    minNotional="1",
    minOrderSize="0.000000001",
    orderbookGranularities=["0.01", "0.1", "1"],
    settlementDecimals=6,
    settlementSymbol="USDT",
    status="LIVE",
    stepSize="0.000000001",
    symbol="BTC/USDT-P",
    tickSize="0.000001",
    underlyingDecimals=8,
    underlyingSymbol="BTC",
)


def _stage_market_order(mock_http, order_id=12345):
    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body={"orderId": order_id}),
            call_validation=lambda call: call.function_name == "send_authorized_request"
            and call.arg_pack[0:2] == ("POST", "/trade/order"),
        )
    )


@pytest.mark.parametrize("direction", [TriggerDirection.HIGH, TriggerDirection.LOW])
def test_place_market_order_trigger_direction_included_in_request(
    mock_http_client, direction
):
    client, mock_http = mock_http_client
    client._future_contracts = {"BTC/USDT-P": BTC_CONTRACT}

    captured = {}

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body={"orderId": 12345}),
            call_validation=lambda call: captured.update({"body": call.arg_pack[2]})
            or (
                call.function_name == "send_authorized_request"
                and call.arg_pack[0:2] == ("POST", "/trade/order")
            ),
        )
    )

    client.place_market_order(
        "BTC/USDT-P",
        0.001,
        Side.BUY,
        0.001,
        trigger_price=85_000,
        trigger_direction=direction,
    )

    assert captured["body"]["triggerDirection"] == direction.value


def test_place_market_order_trigger_direction_absent_when_not_provided(
    mock_http_client,
):
    client, mock_http = mock_http_client
    client._future_contracts = {"BTC/USDT-P": BTC_CONTRACT}

    captured = {}

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body={"orderId": 12345}),
            call_validation=lambda call: captured.update({"body": call.arg_pack[2]})
            or (
                call.function_name == "send_authorized_request"
                and call.arg_pack[0:2] == ("POST", "/trade/order")
            ),
        )
    )

    client.place_market_order(
        "BTC/USDT-P", 0.001, Side.BUY, 0.001, trigger_price=85_000
    )

    assert "triggerDirection" not in captured["body"]


def test_place_market_order_trigger_price_with_tpsl_raises(mock_http_client):
    """The exchange rejects parent orders that are also trigger orders."""
    client, mock_http = mock_http_client
    client._future_contracts = {"BTC/USDT-P": BTC_CONTRACT}

    tpsl = TPSLConfig().add_take_profit(price=90_000)
    with pytest.raises(ValidationError) as exc_info:
        client.place_market_order(
            "BTC/USDT-P",
            0.001,
            Side.BUY,
            0.001,
            trigger_price=85_000,
            tpsl=tpsl,
        )

    assert "trigger price" in str(exc_info.value).lower()
    assert "tpsl" in str(exc_info.value).lower()
