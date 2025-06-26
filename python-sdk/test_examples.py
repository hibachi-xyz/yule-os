import pytest
import asyncio
from examples.example_auth_rest_api import example_auth_rest_api
from examples.example_public_api import example_public_api
from examples.example_ws_market import example_ws_market
from examples.example_ws_account import example_ws_account
from examples.example_ws_trade import example_ws_trade

@pytest.mark.asyncio
async def test_example_public_api():
    example_public_api()

@pytest.mark.asyncio
async def test_example_auth_rest_api():
    example_auth_rest_api()

@pytest.mark.asyncio
async def test_example_ws_market():
    await example_ws_market()

@pytest.mark.asyncio
async def test_example_ws_account():
    await example_ws_account()

@pytest.mark.asyncio
async def test_example_ws_trade():
    await example_ws_trade()