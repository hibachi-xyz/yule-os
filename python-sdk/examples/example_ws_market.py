import asyncio
from hibachi_xyz import HibachiWSMarketClient,WebSocketSubscription,WebSocketSubscriptionTopic,print_data

async def example_ws_market():
    client = HibachiWSMarketClient()
    await client.connect()
    
    await client.subscribe([
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.MARK_PRICE),
        WebSocketSubscription("BTC/USDT-P", WebSocketSubscriptionTopic.TRADES)
    ])

    response = await client.list_subscriptions()
    print("Subscriptions:")
    print_data(response.subscriptions)

    print("Packets:")
    counter = 0
    while counter < 5:
        message = await client.websocket.recv()
        # {"data":{"markPrice":"107248.53515"},"symbol":"BTC/USDT-P","topic":"mark_price"}
        # {"data":{"markPrice":"107248.53515"},"symbol":"BTC/USDT-P","topic":"mark_price"}
        # {"data":{"markPrice":"107248.53515"},"symbol":"BTC/USDT-P","topic":"mark_price"}
        # {"data":{"markPrice":"107248.53071"},"symbol":"BTC/USDT-P","topic":"mark_price"}
        # {"data":{"markPrice":"107248.53071"},"symbol":"BTC/USDT-P","topic":"mark_price"}
        print(message)
        counter += 1

    print("Unsubscribing")
    await client.unsubscribe(response.subscriptions)



if __name__ == "__main__":
    # This code only runs when the file is executed directly
    asyncio.run(example_ws_market())