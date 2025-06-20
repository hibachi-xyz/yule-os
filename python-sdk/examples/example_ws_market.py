import asyncio
from hibachi_xyz import HibachiWSMarketClient,WebSocketSubscription,WebSocketSubscriptionTopic,print_data

async def main():
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
        print(message)
        counter += 1

    print("Unsubscribing")
    await client.unsubscribe(response.subscriptions)

asyncio.run(main())