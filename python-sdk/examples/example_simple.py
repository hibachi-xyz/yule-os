import json
import os
import time

from hibachi_xyz import HibachiApiClient
from dotenv import load_dotenv
load_dotenv()

hibachi = HibachiApiClient(
    api_url= os.environ.get('HIBACHI_API_ENDPOINT', "https://api.hibachi.xyz"),
    data_api_url= os.environ.get('HIBACHI_DATA_API_ENDPOINT', "https://data-api.hibachi.xyz"),
    api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key"),
    account_id = os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id"),
    private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private"),
)

account_info = hibachi.get_account_info()

print(f"Account Balance: {account_info.balance}")
print(f"total Position Notional: {account_info.totalPositionNotional}")

for asset in account_info.assets:
    print(f"Asset: \t\t{asset.symbol} \t\t{asset.quantity}")

for position in account_info.positions:
    print(f"Position: \t{position.symbol} \t{position.quantity}")

