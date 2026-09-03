import pytest

from hibachi_xyz.executors.interface import HttpResponse
from tests.mock_executors import MockSuccessfulOutput
from tests.unit.conftest import load_json_all_cases


@pytest.mark.parametrize("test_data", load_json_all_cases("response.account_trades"))
def test_get_account_trades(mock_http_client, test_data):
    payload, path = test_data
    client, mock_http = mock_http_client

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: (
                call.function_name == "send_authorized_request"
                and call.arg_pack[0:2] == ("GET", "/trade/account/trades?accountId=1")
            ),
        )
    )

    response = client.get_account_trades()

    assert len(response.trades) == len(payload["trades"])
    for trade, raw in zip(response.trades, payload["trades"]):
        assert trade.side == raw["side"]
        assert trade.symbol == raw["symbol"]
        assert trade.price == raw["price"]
        assert trade.quantity == raw["quantity"]
        assert trade.fee == raw["fee"]
        assert trade.id == raw["id"]
        assert trade.orderType == raw["orderType"]
        assert trade.realizedPnl == raw["realizedPnl"]
        assert trade.timestamp == raw["timestamp"]
        assert trade.bidOrderId == raw["bidOrderId"]
        assert trade.askOrderId == raw["askOrderId"]
        # ENG-9132 removed these from the wire entirely (counterparty-identity
        # redaction) - the SDK must not require them.
        assert trade.askAccountId is None
        assert trade.bidAccountId is None


def test_get_account_trades_does_not_raise_when_counterparty_fields_absent(
    mock_http_client,
):
    """Regression test for ENG-9343.

    PR #4244 (ENG-9132) removed askAccountId/bidAccountId from the V1
    GET /trade/account/trades response as a deliberate security fix (traders
    must not be able to identify their counterparty). SDK 0.3.1's AccountTrade
    still declared both as required constructor arguments, so their absence
    raised a TypeError inside create_with(), which get_account_trades() wrapped
    as DeserializationError - breaking every caller on a live exchange response.
    """
    client, mock_http = mock_http_client

    payload = {
        "trades": [
            {
                "side": "SELL",
                "bidOrderId": None,
                "askOrderId": 555111,
                "orderType": "MARKET",
                "symbol": "SOL/USDT-P",
                "quantity": "10.5",
                "price": "142.45",
                "timestamp": 1756296000,
                "id": 987654,
                "realizedPnl": "12.50",
                "fee": "0.75",
                "orderId": 555111,
            }
        ]
    }

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: (
                call.function_name == "send_authorized_request"
            ),
        )
    )

    response = client.get_account_trades()

    trade = response.trades[0]
    assert trade.askAccountId is None
    assert trade.bidAccountId is None
    assert trade.bidOrderId is None
    assert trade.askOrderId == 555111
