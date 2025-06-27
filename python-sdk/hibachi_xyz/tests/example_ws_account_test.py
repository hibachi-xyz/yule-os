import asyncio

from hibachi_xyz import HibachiWSAccountClient, print_data
from hibachi_xyz.env_setup import setup_environment


async def example_ws_account_test(max_messages=3):
    api_endpoint, _, api_key, account_id, *_ = setup_environment()
    ws_url = api_endpoint.replace("https://", "wss://")
    
    client = HibachiWSAccountClient(
        api_endpoint=ws_url,
        api_key=api_key,
        account_id=account_id
    )
    
    await client.connect()
    await client.stream_start()
    
    received = []
    try:
        while len(received) < max_messages:
            message = await client.listen()
            if message:
                received.append(message)
    finally:
        await client.disconnect()

    return received
