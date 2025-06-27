import asyncio

from hibachi_xyz import (HibachiWSMarketClient, WebSocketSubscription,
                         WebSocketSubscriptionTopic, print_data)


async def example_ws_market_test():
    client = HibachiWSMarketClient()
    await client.connect()

    subscriptions = [
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.MARK_PRICE),
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.TRADES)
    ]
    await client.subscribe(subscriptions)

    messages = []

    try:
        for _ in range(5):
            msg = await client.websocket.recv()
            messages.append(msg)
    finally:
        await client.unsubscribe(subscriptions)
        await client.disconnect()

    return messages
