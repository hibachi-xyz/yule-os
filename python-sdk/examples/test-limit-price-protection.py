import os
from hibachi_xyz import HibachiApiClient, HibachiApiError, Side

api_endpoint = "https://api-test.hibachi.xyz"
data_api_endpoint = "https://data-api-test.hibachi.xyz"
api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key")
account_id = os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id")
private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private")

tradeClient = HibachiApiClient(api_endpoint, data_api_endpoint, account_id, api_key, private_key)

max_fees_percent = 0.0005

###### test limit order price protetion ######
market_price = 1850

print("====== Limit orders ======")
(nonce, buy_order_id) = tradeClient.place_limit_order("ETH/USDT-P", 0.001, market_price * 0.93,  Side.BID, max_fees_percent)
print(f"buy within limit: {buy_order_id}")
try:
  tradeClient.place_limit_order("ETH/USDT-P", 0.001, market_price * 1.15,  Side.BID, max_fees_percent)
  assert(False)
except HibachiApiError as err:
    print(f"buy above limit: {err.message}")
result = tradeClient.update_order(buy_order_id, max_fees_percent, price=market_price * 0.92)
print(f"update buy within limit")
try:
  tradeClient.update_order(buy_order_id, max_fees_percent, price=market_price * 1.15)
  assert(False)
except HibachiApiError as err:
    print(f"update buy above limit: {err.message}")

(nonce, sell_order_id) = tradeClient.place_limit_order("ETH/USDT-P", 0.001, market_price * 1.08,  Side.ASK, max_fees_percent)
print(f"sell within limit: {sell_order_id}")
try:
  tradeClient.place_limit_order("ETH/USDT-P", 0.001, market_price * 0.85,  Side.ASK, max_fees_percent)
  assert(False)
except HibachiApiError as err:
    print(f"sell below limit: {err.message}")
result = tradeClient.update_order(sell_order_id, max_fees_percent, price=market_price * 1.07)
print(f"update sell within limit")
try:
  tradeClient.update_order(sell_order_id, max_fees_percent, price=market_price * 0.85)
  assert(False)
except HibachiApiError as err:
    print(f"update sell below limit: {err.message}")

print("====== Trigger Limit orders ======")
trigger_price = 2500
(nonce, buy_order_id) = tradeClient.place_limit_order("ETH/USDT-P", 0.001, trigger_price * 0.93,  Side.BID, max_fees_percent, trigger_price=trigger_price)
print(f"buy within limit: {buy_order_id}")
try:
  tradeClient.place_limit_order("ETH/USDT-P", 0.001, trigger_price * 1.15,  Side.BID, max_fees_percent, trigger_price=trigger_price)
  assert(False)
except HibachiApiError as err:
    print(f"buy above limit: {err.message}")
result = tradeClient.update_order(buy_order_id, max_fees_percent, price=trigger_price * 0.92)
print(f"update price buy within limit")
result = tradeClient.update_order(buy_order_id, max_fees_percent, trigger_price=trigger_price * 1.5)
print(f"update trigger buy within limit")
try:
  tradeClient.update_order(buy_order_id, max_fees_percent, price=trigger_price * 1.5 * 1.25)
  assert(False)
except HibachiApiError as err:
    print(f"update price buy above limit: {err.message}")
try:
  tradeClient.update_order(buy_order_id, max_fees_percent, trigger_price=trigger_price * 0.5)
  assert(False)
except HibachiApiError as err:
    print(f"update trigger buy above limit: {err.message}")

(nonce, sell_order_id) = tradeClient.place_limit_order("ETH/USDT-P", 0.001, trigger_price * 1.08,  Side.ASK, max_fees_percent, trigger_price=trigger_price)
print(f"sell within limit: {sell_order_id}")
try:
  tradeClient.place_limit_order("ETH/USDT-P", 0.001, trigger_price * 0.85,  Side.ASK, max_fees_percent, trigger_price=trigger_price)
  assert(False)
except HibachiApiError as err:
    print(f"sell below limit: {err.message}")
result = tradeClient.update_order(sell_order_id, max_fees_percent, price=trigger_price * 1.07)
print(f"update price sell within limit")
result = tradeClient.update_order(sell_order_id, max_fees_percent, trigger_price=trigger_price * 0.5)
print(f"update trigger sell within limit")
try:
  tradeClient.update_order(sell_order_id, max_fees_percent, price=trigger_price * 0.5 * 0.85)
  assert(False)
except HibachiApiError as err:
    print(f"update price sell below limit: {err.message}")
try:
  tradeClient.update_order(sell_order_id, max_fees_percent, trigger_price=trigger_price * 1.5)
  assert(False)
except HibachiApiError as err:
    print(f"update trigger sell below limit: {err.message}")

