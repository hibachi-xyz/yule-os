import asyncio
import json
import os
import time
from dotenv import load_dotenv
import pytest

from hibachi_xyz.api_ws_market import HibachiWSMarketClient
from hibachi_xyz.api_ws_trade import HibachiWSTradeClient
from hibachi_xyz.api_ws_account import HibachiWSAccountClient

from hibachi_xyz.types import (
    OrderModifyParams, Position, WebSocketSubscription, OrderPlaceParams, WebSocketOrderCancelParams,
    WebSocketOrderModifyParams, WebSocketOrderStatusParams, WebSocketOrdersStatusParams,
    WebSocketOrdersCancelParams, WebSocketBatchOrder, WebSocketOrdersBatchParams,
    WebSocketStreamStartParams, WebSocketStreamPingParams, WebSocketStreamStopParams,
    WebSocketSubscriptionTopic, OrderType, Side, OrderStatus, AccountSnapshot, OrderPlaceParams, OrderPlaceResponse, Nonce
)

from hibachi_xyz.helpers import print_data

load_dotenv()

api_endpoint = os.environ.get('HIBACHI_API_ENDPOINT', "https://api.hibachi.xyz")
data_api_endpoint = os.environ.get('HIBACHI_DATA_API_ENDPOINT', "https://data-api.hibachi.xyz")
account_id = int(os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id"))
private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private")
api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key")
public_key = os.environ.get('HIBACHI_PUBLIC_KEY', "your-public")

@pytest.mark.asyncio
async def test_market_websocket():
    
    client = HibachiWSMarketClient(data_api_endpoint.replace("https://", "wss://"))

    await client.connect()
    response = await client.list_subscriptions()
 
    assert len(response.subscriptions) == 0

    subscriptions = [
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.MARK_PRICE),
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.TRADES)
    ]
    
    await client.subscribe(subscriptions)

    response = await client.list_subscriptions()
    
    assert len(response.subscriptions) == 2
    countmatches = 0
    for sub in response.subscriptions:
        if sub.topic == WebSocketSubscriptionTopic.MARK_PRICE:
            countmatches += 1
            assert sub.symbol == "BTC/USDT-P"
        if sub.topic == WebSocketSubscriptionTopic.TRADES:
            countmatches += 1
            assert sub.symbol == "BTC/USDT-P"
    assert countmatches == 2
    
    counter = 0
    while counter < 5:
        message = await client.websocket.recv()
        print(message)
        counter += 1

    await client.unsubscribe(response.subscriptions)
    response = await client.list_subscriptions()
    assert len(response.subscriptions) == 0

@pytest.mark.asyncio
async def test_trade_websocket():
    client = HibachiWSTradeClient(
        api_url=api_endpoint, 
        data_api_url=data_api_endpoint,
        api_key=api_key, 
        account_id=account_id, 
        account_public_key=public_key,
        private_key=private_key
    )
    await client.connect()    

    client.api.cancel_all_orders()

    # websocket orders status
    orders_start = await client.get_orders_status()
    print_data(orders_start)

    # confirm list is empty over websockets
    assert len(orders_start.result) == 0

    # confirm with rest api
    orders_rest = client.api.get_pending_orders()
    print_data(orders_rest)

    assert len(orders_rest.orders) == len(orders_start.result)
    assert len(orders_rest.orders) == 0

    # place an order using REST
    current_price = client.api.get_prices("BTC/USDT-P")
    print(f"current_price: {current_price}")

    start_order_count = len(client.api.get_pending_orders().orders)

    (nonce, order_id) = client.api.place_limit_order(
        symbol="BTC/USDT-P", 
        quantity=0.0001, 
        side=Side.ASK, 
        max_fees_percent=0.005, 
        price=float(current_price.askPrice) *1.05
    )
    
    # websocket orders status
    orders_start = await client.get_orders_status()

    # confirm with rest api
    orders_rest = client.api.get_pending_orders()

    assert len(orders_rest.orders) == len(orders_start.result)
    assert len(orders_rest.orders) == 1

    # test cancel using websocket

    result_of_cancel_all_orders = await client.cancel_all_orders()


    assert len(client.api.get_pending_orders().orders) == 0

    # all orders cleared again...

    price_before = float(current_price.askPrice) * 1.05
    # place an order using websocket
    (nonce, order_id) = await client.place_order(OrderPlaceParams(
        symbol="BTC/USDT-P",
        quantity=0.0001,
        side=Side.BUY,
        maxFeesPercent=0.0005,
        orderType=OrderType.LIMIT,
        price=price_before,
        orderFlags=None,
        trigger_price=None,
        twap_config=None
    ))

    assert nonce is not None
    assert order_id is not None

    assert isinstance(nonce, Nonce)
    assert isinstance(order_id , int)

    print(f"place new order nonce: {nonce} order_id: {order_id}")

    order = await client.get_order_status(order_id)

    assert order.result.orderId
    
    price_after = float(current_price.askPrice) * 1.075

    # ---- test using rest
    order_details = client.api.get_order_details(order_id=int(order.result.orderId))

    print("FETCHED ORDER USING REST API:")
    print_data(order_details)

    assert order_details.orderId == order.result.orderId

    print("TESTING WITH WEBSOCKET")

    # ---- modify using websocket:
    
    modify_result = await client.modify_order(
        order=order.result,
        quantity=0.0001, 
        price=price_after,
        side=order.result.side,
        maxFeesPercent=0.0005,   
        nonce=nonce
    )

    # assert modify_result.get("status") == 200

    print("confirm order is in orders status")
    orders_end = await client.get_orders_status()
    print_data(orders_end)

    assert len(orders_end.result) == 1
    assert orders_end.result[0].orderId == order.result.orderId

    

@pytest.mark.asyncio
async def test_account_websocket():
    client = HibachiWSAccountClient(
        api_endpoint=api_endpoint.replace("https://", "wss://"), api_key=api_key, account_id=account_id)
    await client.connect()
    result_start = await client.stream_start()
    assert isinstance(result_start.listenKey,str)
    assert isinstance(result_start.accountSnapshot, AccountSnapshot)
    assert len(result_start.accountSnapshot.positions) > 0
    first_position = result_start.accountSnapshot.positions[0]
    assert isinstance(first_position, Position)

    