import pytest

from hibachi_xyz.executors.interface import HttpResponse
from hibachi_xyz.types import TriggerDirection
from tests.mock_executors import MockSuccessfulOutput
from tests.unit.conftest import load_json_all_cases


@pytest.mark.parametrize("test_data", load_json_all_cases("response.pending_orders"))
def test_get_pending_orders(mock_http_client, test_data):
    payload, path = test_data
    client, mock_http = mock_http_client

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name == "send_authorized_request"
            and call.arg_pack[0:2] == ("GET", "/trade/orders?accountId=1"),
        )
    )

    response = client.get_pending_orders()

    assert len(response.orders) == len(payload)
    for order, raw in zip(response.orders, payload):
        assert order.orderId == int(raw["orderId"])
        assert order.symbol == raw["symbol"]
        assert order.side.value == raw["side"]
        assert order.status.value == raw["status"]
        assert order.orderType.value == raw["orderType"]
        expected_direction = (
            TriggerDirection(raw["triggerDirection"])
            if raw.get("triggerDirection")
            else None
        )
        assert order.triggerDirection == expected_direction


def test_get_pending_orders_trigger_direction_high(mock_http_client):
    client, mock_http = mock_http_client

    payload = [
        {
            "accountId": 1,
            "availableQuantity": "0.001",
            "orderId": "99001",
            "orderType": "MARKET",
            "side": "BUY",
            "status": "PLACED",
            "symbol": "BTC/USDT-P",
            "totalQuantity": "0.001",
            "triggerPrice": "90000.00",
            "triggerDirection": "HIGH",
        }
    ]

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name
            == "send_authorized_request",
        )
    )

    response = client.get_pending_orders()

    assert response.orders[0].triggerDirection == TriggerDirection.HIGH


def test_get_pending_orders_trigger_direction_low(mock_http_client):
    client, mock_http = mock_http_client

    payload = [
        {
            "accountId": 1,
            "availableQuantity": "0.001",
            "orderId": "99002",
            "orderType": "MARKET",
            "side": "SELL",
            "status": "PLACED",
            "symbol": "ETH/USDT-P",
            "totalQuantity": "0.001",
            "triggerPrice": "2000.00",
            "triggerDirection": "LOW",
        }
    ]

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name
            == "send_authorized_request",
        )
    )

    response = client.get_pending_orders()

    assert response.orders[0].triggerDirection == TriggerDirection.LOW


def test_get_pending_orders_trigger_direction_absent_when_not_provided(
    mock_http_client,
):
    client, mock_http = mock_http_client

    payload = [
        {
            "accountId": 1,
            "availableQuantity": "0.005",
            "orderId": "99003",
            "orderType": "LIMIT",
            "side": "BUY",
            "status": "PLACED",
            "symbol": "BTC/USDT-P",
            "price": "80000.00",
            "totalQuantity": "0.005",
        }
    ]

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name
            == "send_authorized_request",
        )
    )

    response = client.get_pending_orders()

    assert response.orders[0].triggerDirection is None
