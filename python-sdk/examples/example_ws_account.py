import asyncio
from hibachi_xyz import HibachiWSAccountClient,WebSocketSubscription,WebSocketSubscriptionTopic,print_data

async def main():
    client = HibachiWSAccountClient(api_key="your-api-key", account_id=123)

    await client.connect()
    result_start = await client.stream_start()

    print_data(result_start)

    print("Listening:")
    counter = 0
    while counter < 5:
        message = await client.listen()
        print_data(message)
        counter += 1  

asyncio.run(main())