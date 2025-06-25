# Hibachi Python SDK

The official Python SDK for interacting with the Hibachi cryptocurrency exchange API.

[Official API Docs](https://api-doc.hibachi.xyz/)

# Get Started

```bash
python3 -m venv myapp
cd myapp
./bin/pip install hibachi-xyz websockets prettyprinter dotenv
```

Create `main.py`

```python
from hibachi_xyz import HibachiApiClient
from dotenv import load_dotenv
import os

load_dotenv()

hibachi = HibachiApiClient()
exchange_info = hibachi.get_exchange_info()
print(exchange_info)
```

## Authentication

Create a `.env` file and enter your values from hibachi. Please see https://hibachi-docs.redocly.app/api/authorization for more information.

```
HIBACHI_API_ENDPOINT="https://api.hibachi.xyz"
HIBACHI_DATA_API_ENDPOINT="https://data-api.hibachi.xyz"
HIBACHI_API_KEY="your_api_key_here"
HIBACHI_PRIVATE_KEY="your_private_key_here"
HIBACHI_PUBLIC_KEY="your_public_key_here"
HIBACHI_ACCOUNT_ID="your_account_id_here"
```

```python
# ensure .env has the values set.
hibachi = HibachiApiClient(    
    api_url= os.environ.get('HIBACHI_API_ENDPOINT'),
    data_api_url= os.environ.get('HIBACHI_DATA_API_ENDPOINT'),
    api_key = os.environ.get('HIBACHI_API_KEY'),
    account_id = os.environ.get('HIBACHI_ACCOUNT_ID'),
    private_key = os.environ.get('HIBACHI_PRIVATE_KEY'),
)

account_info = hibachi.get_account_info()
print(f"Account Balance: {account_info.balance}")
print(f"total Position Notional: {account_info.totalPositionNotional}")
```

Once you can see your account balance you can proceed with the below examples or specific documentation. Let us know if you need any help!

# Examples

See how to use the Python SDK from working code:

[Simple Example](./python-sdk/examples/example_simple.py)   
[Extended Example](./python-sdk/examples/api_examples.py)   
[REST Tests](./test_hibachi.py)   
[Websocket Tests](./test_websocket.py)   

[Websocket Account Docs ](#api_ws_market.HibachiWSAccountClient)
[Websocket Account Example](./python-sdk/examples/example_ws_account.py)

[Websocket Market Docs ](#api_ws_market.HibachiWSMarketClient)
[Websocket Market Example](./python-sdk/examples/example_ws_market.py)

[Websocket Trade Docs ](#api_ws_market.HibachiWSTradeClient)
[Websocket Trade Example](./python-sdk/examples/example_ws_trade.py)


## Environment Variables

The SDK supports the following environment variables. You can create a `.env` file and update values. Keep your keys safe.

```sh
# Default API endpoint
HIBACHI_API_ENDPOINT="https://api.hibachi.xyz"
# Default data API endpoint
HIBACHI_DATA_API_ENDPOINT="https://data-api.hibachi.xyz"
# Your API key
HIBACHI_API_KEY=""
# Your account ID
HIBACHI_ACCOUNT_ID=""
# Your private key
HIBACHI_PRIVATE_KEY=""
```

# API Reference

| Method                   | API Endpoint                                                                            | Description                                                    |
|--------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------|
| [get_exchange_info](#api.HibachiApiClient.get_exchange_info)              | /market/exchange-info                  | Return Exchange information, contracts and maintenance status. |
| [get_inventory](#api.HibachiApiClient.get_inventory)                      | /market/inventory                      | Similar to exchange info, includes price data                  |
| [get_prices](#api.HibachiApiClient.get_prices)                            | /market/data/prices                    | Get the price and funding information for a future contract.   |
| [get_stats](#api.HibachiApiClient.get_stats)                              | /market/data/stats                     | Get 24h high/low/volume for a future contract.                 |
| [get_trades](#api.HibachiApiClient.get_trades)                            | /market/data/trades                    | Get recent trades from all users for one future contract.      |
| [get_klines](#api.HibachiApiClient.get_klines)                            | /market/data/klines                    | Get the candlesticks for a future contract.                    |
| [get_open_interest](#api.HibachiApiClient.get_open_interest)              | /market/data/open-interest             | Get the open interest for one future contract.                 |
| [get_orderbook](#api.HibachiApiClient.get_orderbook)                      | /market/data/orderbook                 | Get the orderbook price levels.                                |
| [get_capital_balance](#api.HibachiApiClient.get_capital_balance)          | /capital/balance                       | Get the balance of your account.                               | 
| [get_capital_history](#api.HibachiApiClient.get_capital_history)          | /capital/history                       | Get the deposit and withdraw history of your account.          |
| [withdraw](#api.HibachiApiClient.withdraw)                                | /capital/withdraw                      | Submit a withdraw request.                                     |  
| [transfer](#api.HibachiApiClient.transfer)                                | /capital/transfer                      | Submit a transfer request.                                     |
| [get_deposit_info](#api.HibachiApiClient.get_deposit_info)                | /capital/deposit-info                  | Get deposit address                                            |   
| [get_account_info](#api.HibachiApiClient.get_account_info)                | /trade/account/info                    | Get account information/details                                |
| [get_account_trades](#api.HibachiApiClient.get_account_trades)            | /trade/account/trades                  | Get the trades history of your account.                        |
| [get_settlements_history](#api.HibachiApiClient.get_settlements_history)  | /trade/account/settlements_history     | You can obtain the history of settled trades                   |
| [get_pending_orders](#api.HibachiApiClient.get_pending_orders)            | /trade/orders                          | Get the pending orders of your account.                        |
| [get_order_details](#api.HibachiApiClient.get_order_details)              | /trade/order                           | Get the details about your one particular order.               |
| [place_limit_order](#api.HibachiApiClient.place_limit_order)              | /trade/order                           | Submit a new limit order.                                      |
| [place_market_order](#api.HibachiApiClient.place_market_order)            | /trade/order                           | Submit a new market order.                                     |
| [batch_orders](#api.HibachiApiClient.batch_orders)                        | /trade/orders                          | Submit multiple order requests for an account. Place or Modify |
| [update_order](#api.HibachiApiClient.update_order)                        | /trade/order                           | Modify an existing order.                                      |
| [cancel_order](#api.HibachiApiClient.cancel_order)                        | /trade/order                           | Remove an existing order.                                      |
| [cancel_all_orders](#api.HibachiApiClient.cancel_all_orders)              | /trade/orders                          | Allows you to batch cancel all open orders for an account.     |

# Websocket API

[Market Websocket](#api_ws_market.HibachiWSMarketClient)
[Trade Websocket](#api_ws_trade.HibachiWSTradeClient)
[Account Websocket](#api_ws_account.HibachiWSAccountClient)
