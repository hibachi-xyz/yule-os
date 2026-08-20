from unittest.mock import Mock, patch

import pytest
import requests

from hibachi_xyz.errors import TransportTimeoutError
from hibachi_xyz.executors.requests import DEFAULT_TIMEOUT, RequestsHttpExecutor


def test_simple_request_passes_configured_timeout() -> None:
    response = Mock(status_code=200, content=b"{}")
    executor = RequestsHttpExecutor(
        data_api_url="https://data.example",
        timeout_seconds=7.5,
    )

    with patch("requests.get", return_value=response) as request:
        executor.send_simple_request("/health")

    request.assert_called_once_with(
        "https://data.example/health",
        headers={"Hibachi-Client": request.call_args.kwargs["headers"]["Hibachi-Client"]},
        timeout=7.5,
    )


def test_authorized_request_passes_default_timeout() -> None:
    response = Mock(status_code=200, content=b"{}")
    executor = RequestsHttpExecutor(
        api_url="https://api.example",
        api_key="test-key",
    )

    with patch("requests.request", return_value=response) as request:
        executor.send_authorized_request("POST", "/orders", {"x": 1})

    assert request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT
    assert request.call_args.args[:2] == ("POST", "https://api.example/orders")


@pytest.mark.parametrize("method", ["send_simple_request", "send_authorized_request"])
def test_requests_timeout_is_translated(method: str) -> None:
    executor = RequestsHttpExecutor(timeout_seconds=3.0)
    patch_target = "requests.get" if method == "send_simple_request" else "requests.request"

    with patch(patch_target, side_effect=requests.Timeout("timed out")):
        with pytest.raises(TransportTimeoutError) as raised:
            if method == "send_simple_request":
                executor.send_simple_request("/health")
            else:
                executor.send_authorized_request("GET", "/health")

    assert raised.value.timeout_seconds == 3.0
