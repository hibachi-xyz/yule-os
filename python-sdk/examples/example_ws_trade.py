import asyncio
import os
from hibachi_xyz import HibachiWSTradeClient, print_data

from dotenv import load_dotenv
load_dotenv()

api_endpoint = os.environ.get('HIBACHI_API_ENDPOINT', "https://api.hibachi.xyz")
data_api_endpoint = os.environ.get('HIBACHI_DATA_API_ENDPOINT', "https://data-api.hibachi.xyz")
account_id = int(os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id"))
private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private")
api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key")
public_key = os.environ.get('HIBACHI_PUBLIC_KEY', "your-public")

async def main():
    client = HibachiWSTradeClient(
        api_url=api_endpoint, 
        api_key=api_key, 
        account_id=account_id, 
        account_public_key=public_key,
        private_key=private_key
    )

    await client.connect()    
    orders = await client.get_orders_status()
    first_order = orders.result[0]

    # single order
    order = await client.get_order_status(first_order.orderId)
    print_data(order)

    # client.api.set_private_key(private_key)
    modify_result = await client.modify_order(
        order=order.result,
        quantity=float("0.002"), 
        price=str(float("93500.0")),
        side=order.result.side,
        maxFeesPercent=float("0.00045"),
    )

    print_data(modify_result)

asyncio.run(main())