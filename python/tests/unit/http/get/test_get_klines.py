import pytest

from hibachi_xyz.executors.interface import HttpResponse
from hibachi_xyz.types import Interval
from tests.mock_executors import MockSuccessfulOutput
from tests.unit.conftest import load_json_all_cases


@pytest.mark.parametrize("test_data", load_json_all_cases("response.klines"))
def test_get_klines(mock_http_client, test_data):
    payload, path = test_data
    client, mock_http = mock_http_client

    symbol = "ETH/USDT-P"
    interval = Interval.ONE_HOUR

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name == "send_simple_request"
            and call.arg_pack
            == (f"/market/data/klines?symbol={symbol}&interval={interval.value}",),
        )
    )

    klines_response = client.get_klines(symbol, interval)

    # KlinesResponse assertions
    assert len(klines_response.klines) == len(payload["klines"])

    for kline, payload_kline in zip(klines_response.klines, payload["klines"]):
        assert kline.close == payload_kline["close"]
        assert kline.high == payload_kline["high"]
        assert kline.low == payload_kline["low"]
        assert kline.open == payload_kline["open"]
        assert kline.interval == payload_kline["interval"]
        assert kline.timestamp == payload_kline["timestamp"]
        assert kline.volumeNotional == payload_kline["volumeNotional"]


@pytest.mark.parametrize("test_data", load_json_all_cases("response.klines"))
def test_get_klines_with_time_range(mock_http_client, test_data):
    payload, path = test_data
    client, mock_http = mock_http_client

    symbol = "ETH/USDT-P"
    interval = Interval.ONE_HOUR
    from_ms = 1700000000000
    to_ms = 1700003600000

    mock_http.stage_output(
        MockSuccessfulOutput(
            output=HttpResponse(status=200, body=payload),
            call_validation=lambda call: call.function_name == "send_simple_request"
            and call.arg_pack
            == (
                f"/market/data/klines?symbol={symbol}&interval={interval.value}&fromMs={from_ms}&toMs={to_ms}",
            ),
        )
    )

    klines_response = client.get_klines(symbol, interval, from_ms=from_ms, to_ms=to_ms)

    assert len(klines_response.klines) == len(payload["klines"])
