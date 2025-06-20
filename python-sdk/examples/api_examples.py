import json
import os
import time

from hibachi_xyz import get_version, HibachiApiClient, HibachiApiError, Interval, Side, TWAPConfig, TWAPQuantityMode, CreateOrder, UpdateOrder, CancelOrder, print_data

api_endpoint = os.environ.get('HIBACHI_API_ENDPOINT', "https://api.hibachi.xyz")
data_api_endpoint = os.environ.get('HIBACHI_DATA_API_ENDPOINT', "https://data-api.hibachi.xyz")
api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key")
account_id = os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id")
private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private")

print(f"Hibachi SDK Version: {get_version()}")

client = HibachiApiClient(api_endpoint, data_api_endpoint, api_key=api_key, account_id=account_id)

# These endpoints do not require authentication
print_data(client.get_exchange_info())
print_data(client.get_prices("BTC/USDT-P"))
print_data(client.get_stats("BTC/USDT-P"))
print_data(client.get_trades("BTC/USDT-P"))
print_data(client.get_klines("BTC/USDT-P", Interval.ONE_MINUTE))
print_data(client.get_open_interest("BTC/USDT-P"))
print_data(client.get_orderbook("SOL/USDT-P", 5, 0.01))

# Setup authentication
# client.set_account_id(account_id)
# client.set_api_key(api_key)

print_data(client.get_account_info())
print_data(client.get_account_trades())
print_data(client.get_settlements_history())
print_data(client.get_pending_orders())

###                         WARNING                          ###
### The below part will try to create orders and make trades ###
### Use at your own risk                                     ###

# For manipulating orders, the private key is also required
client.set_private_key(private_key)

# max_fees_percent is required for most actions related to orders, it must be at least as much as returned in the exchange_info
max_fees_percent = 0.0005

# Market buy order Side.BUY and Side.BID are the same, both can be used
# On a successful order placement the call returns the nonce and the order_id of the created order
(nonce, order_id) = client.place_market_order("BTC/USDT-P", 0.0001, Side.BUY, max_fees_percent)
# Market sell order Side.SELL and Side.ASK are the same, both can be used
(nonce, order_id) = client.place_market_order("BTC/USDT-P", 0.0001, Side.SELL, max_fees_percent)

# Order creation support an optional creation deadline parameter, the order will be rejected if cannot be placed within deadline seconds
(nonce, order_id) = client.place_market_order("BTC/USDT-P", 0.0001, Side.BID, max_fees_percent, creation_deadline=2)

# A more advanced order type is the trigger order, the actual order is placed only when the market price touches or crosses the trigger price
(nonce, order_id) = client.place_market_order("BTC/USDT-P", 0.0001, Side.ASK, max_fees_percent, trigger_price=1_000_000)

# Market orders with considerable quantity can be automatically spread out in time by smaller, scheduled orders
# The first parameter is duration of the spread in minutes
twap_config = TWAPConfig(2, TWAPQuantityMode.FIXED)
(nonce, order_id) = client.place_market_order("SOL/USDT-P", 1, Side.BID, max_fees_percent, twap_config=twap_config)

# Either the order_id or the nonce can be used to query the order details
print_data(client.get_order_details(order_id=order_id))
print_data(client.get_order_details(nonce=nonce))

# Limit orders can be placed similarly to market orders
(nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, 80_000, Side.BUY, max_fees_percent)
(nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, 80_000, Side.SELL, max_fees_percent)
(nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, 80_000, Side.BID, max_fees_percent, creation_deadline=2)
(nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, 1_001_000, Side.ASK, max_fees_percent, trigger_price=1_000_000)

# Pending or partially filled orders can be updated using the order_id
# Quantity, price and trigger price can be updated separately or any number of them at once
# The single order update request is convenient, but does two requests behind the curtains
# First it will downlowd the order details of the order to be updated to get all data to create a correct signature
print_data(client.get_order_details(order_id=order_id))
client.update_order(order_id, max_fees_percent, quantity=0.002)
print_data(client.get_order_details(order_id=order_id))
client.update_order(order_id, max_fees_percent, price=1_050_000)
print_data(client.get_order_details(order_id=order_id))
client.update_order(order_id, max_fees_percent, trigger_price=1_100_000)
print_data(client.get_order_details(order_id=order_id))
client.update_order(order_id, max_fees_percent, quantity=0.001, price=1_210_000, trigger_price=1_250_000)
print_data(client.get_order_details(order_id=order_id))

# Orders can be cancelled one by one
client.cancel_order(order_id=order_id)
# Or all at once
client.cancel_all_orders()

(nonce, limit_order_id) = client.place_limit_order("BTC/USDT-P", 0.001, 6_000, Side.BID, max_fees_percent)
(nonce, trigger_limit_order_id) = client.place_limit_order("BTC/USDT-P", 0.001, 90_000, Side.ASK, max_fees_percent, trigger_price=90_100)
(nonce, trigger_market_order_id) = client.place_market_order("BTC/USDT-P", 0.001, Side.ASK, max_fees_percent, trigger_price=90_100)

# Creating, updating and cancelling orders can be done in a batch
# This requires knowing all details of the existing orders, there is no shortcut for update order details
response = client.batch_orders([
    # Simple market order
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent),
    # Simple limit order
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent, price=90_000),
    # Trigger market order
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent, trigger_price=85_000),
    # Trigger limit order
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent, price=84_750, trigger_price=85_000),
    # TWAP order
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent, twap_config=TWAPConfig(5, TWAPQuantityMode.FIXED)),
    # Market order, only valid if placed within two seconds
    CreateOrder("BTC/USDT-P", Side.BUY, 0.001, max_fees_percent, creation_deadline=2),
    # Limit order, only valid if placed within one seconds
    CreateOrder("BTC/USDT-P", Side.BUY, 0.001, max_fees_percent, price=90_000, creation_deadline=1),
    # Trigger market order, only valid if placed within three seconds
    CreateOrder("BTC/USDT-P", Side.BUY, 0.001, max_fees_percent, trigger_price=85_000, creation_deadline=3),
    # Trigger limit order, only valid if placed within five seconds
    CreateOrder("BTC/USDT-P", Side.BUY, 0.001, max_fees_percent, price=75_250, trigger_price=75_000, creation_deadline=5),
    # TWAP order only valid if placed within two seconds
    CreateOrder("BTC/USDT-P", Side.SELL, 0.001, max_fees_percent, twap_config=TWAPConfig(5, TWAPQuantityMode.FIXED), creation_deadline=2),
    # Update limit order
    # Need to fill all relevant optional parameters
    UpdateOrder(limit_order_id, "BTC/USDT-P", Side.BUY, 0.001, max_fees_percent, price=60_000),
    # update trigger limit order
    # Need to fill all relevant optional parameters
    UpdateOrder(trigger_limit_order_id, "BTC/USDT-P", Side.ASK, 0.002, max_fees_percent, price=94_000, trigger_price=94_500),
    # update trigger market order
    # Need to fill all relevant optional parameters
    UpdateOrder(trigger_market_order_id, "BTC/USDT-P", Side.ASK, 0.001, max_fees_percent, trigger_price=93_000),
    # Cancel order
    CancelOrder(order_id=limit_order_id),
    CancelOrder(nonce=nonce),
])

client.cancel_all_orders()
