from dataclasses import asdict, dataclass
import json
import os
import time
import asyncio
from prettyprinter import pformat
import websockets
from typing import List, Union

from hibachi_xyz import get_version, HibachiApiClient, HibachiApiError, Interval, TWAPConfig, TWAPQuantityMode, CreateOrder, UpdateOrder, CancelOrder
from hibachi_xyz.types import FundingRateEstimation, Order, Side, OrderStatus, OrderType, PriceResponse, StatsResponse, TradesResponse, Trade, TakerSide
from hibachi_xyz.helpers import format_maintenance_window, get_next_maintenance_window, get_withdrawal_fee_for_amount, print_data

from hibachi_xyz.types import ExchangeInfo, FeeConfig, FutureContract, MaintenanceWindow, WithdrawalLimit, KlinesResponse, Kline, OpenInterestResponse, OrderBook, OrderBookLevel, AccountInfo, Asset, Position, AccountTradesResponse, AccountTrade, SettlementsResponse, Settlement, PendingOrdersResponse, Order, CapitalHistory, Transaction, WithdrawResponse, DepositInfo, CapitalBalance, InventoryResponse, CrossChainAsset, Market, TradingTier

from eth_keys import keys


from dotenv import load_dotenv

load_dotenv()



def is_convertible_to_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False

api_endpoint = os.environ.get('HIBACHI_API_ENDPOINT', "https://api.hibachi.xyz")
data_api_endpoint = os.environ.get('HIBACHI_DATA_API_ENDPOINT', "https://data-api.hibachi.xyz")
api_key = os.environ.get('HIBACHI_API_KEY', "your-api-key")
account_id = int(os.environ.get('HIBACHI_ACCOUNT_ID', "your-account-id"))
private_key = os.environ.get('HIBACHI_PRIVATE_KEY', "your-private")
public_key = os.environ.get('HIBACHI_PUBLIC_KEY', "your-public")

def test_get_version():
    ver = get_version()    
    assert isinstance(ver, str)

def test_exchange_info():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None

    exch_info = client.get_exchange_info()
    assert exch_info != None

    
    
    assert isinstance(exch_info, ExchangeInfo)
    
    assert exch_info.feeConfig != None
    assert isinstance(exch_info.feeConfig, FeeConfig)

    assert exch_info.futureContracts[0] != None
    assert isinstance(exch_info.futureContracts[0], FutureContract)

    
    assert isinstance(exch_info.futureContracts[0].displayName, str)

    assert exch_info.instantWithdrawalLimit != None
    assert isinstance(exch_info.instantWithdrawalLimit, WithdrawalLimit)

    assert exch_info.maintenanceWindow != None
    assert isinstance(exch_info.maintenanceWindow, List)
    assert isinstance(exch_info.status, str)

    fee = get_withdrawal_fee_for_amount(exch_info, 1000)
    assert fee == 0.002

    next_maintainance_window = get_next_maintenance_window(exch_info)

    if next_maintainance_window != None:
        assert isinstance(next_maintainance_window, MaintenanceWindow)
   
def test_get_prices():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    prices = client.get_prices("BTC/USDT-P")    
    # print_data(client.get_prices("BTC/USDT-P"))

    assert isinstance(prices.askPrice, str)
    assert isinstance(prices.bidPrice, str)
    assert isinstance(prices.fundingRateEstimation, FundingRateEstimation)
    assert isinstance(prices.markPrice, str)
    assert isinstance(prices.spotPrice, str)
    assert isinstance(prices.symbol, str)
    assert isinstance(prices.tradePrice, str)

def test_get_stats():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    testsymbol = "BTC/USDT-P"
    stats = client.get_stats(testsymbol)
    
    assert isinstance(stats, StatsResponse)
    assert isinstance(stats.high24h, str)
    assert isinstance(stats.low24h, str)
    assert isinstance(stats.symbol, str)
    assert isinstance(stats.volume24h, str)
    assert float(stats.high24h) > 0
    assert float(stats.low24h) > 0
    assert float(stats.volume24h) > 0
    assert stats.symbol == testsymbol

def test_get_trades():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    trades_response = client.get_trades("BTC/USDT-P")
    
    assert isinstance(trades_response, TradesResponse)
    assert isinstance(trades_response.trades, list)

    if len(trades_response.trades) > 0:
    
        # Test first trade
        trade = trades_response.trades[0]
        assert isinstance(trade, Trade)
        assert isinstance(trade.price, str)
        assert isinstance(trade.quantity, str)
        assert isinstance(trade.takerSide, TakerSide)
        assert isinstance(trade.timestamp, int)
        
        # Value validation
        assert float(trade.price) > 0
        assert float(trade.quantity) > 0
        assert trade.takerSide in (TakerSide.Buy, TakerSide.Sell)
        assert trade.timestamp > 0

def test_get_klines():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    klines_response = client.get_klines("BTC/USDT-P", Interval.ONE_WEEK)
    
    assert isinstance(klines_response, KlinesResponse)
    assert isinstance(klines_response.klines, list)
    
    # Test first kline
    if len(klines_response.klines) > 0:        
        kline = klines_response.klines[0]
        assert isinstance(kline, Kline)
        assert isinstance(kline.close, str)
        assert isinstance(kline.high, str)
        assert isinstance(kline.low, str)
        assert isinstance(kline.open, str)
        assert isinstance(kline.interval, str)
        assert isinstance(kline.timestamp, int)
        assert isinstance(kline.volumeNotional, str)
        
        # Value validation
        assert float(kline.close) > 0
        assert float(kline.high) > 0
        assert float(kline.low) > 0
        assert float(kline.open) > 0
        assert kline.interval in ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
        assert kline.timestamp > 0
        assert float(kline.volumeNotional) >= 0
        
        # Logical validation
        assert float(kline.high) >= float(kline.low)
        assert float(kline.high) >= float(kline.open)
        assert float(kline.high) >= float(kline.close)
        assert float(kline.low) <= float(kline.open)
        assert float(kline.low) <= float(kline.close)

def test_get_open_interest():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    open_interest = client.get_open_interest("BTC/USDT-P")
    
    assert isinstance(open_interest, OpenInterestResponse)
    assert isinstance(open_interest.totalQuantity, str)
    assert float(open_interest.totalQuantity) >= 0

def test_get_orderbook():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    orderbook = client.get_orderbook("SOL/USDT-P", 5, 0.01)
    
    assert isinstance(orderbook, OrderBook)
    assert isinstance(orderbook.ask, list)
    assert isinstance(orderbook.bid, list)

    if len(orderbook.ask) > 0:
        first_ask = orderbook.ask[0]
        assert isinstance(first_ask, OrderBookLevel)
        assert float(first_ask.price) > 0
        assert float(first_ask.quantity) > 0

    if len(orderbook.bid) > 0:
        first_bid = orderbook.bid[0]
        assert isinstance(first_bid, OrderBookLevel)
        assert float(first_bid.price) > 0
        assert float(first_bid.quantity) > 0
    
def test_get_account_info():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert account_id != "your-account-id"
    assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)
    
    accountinfo = client.get_account_info()

    assert isinstance(accountinfo, AccountInfo)
    assert isinstance(accountinfo.assets, list)
    assert isinstance(accountinfo.positions, list)
    
    if len(accountinfo.assets) > 0:
        asset = accountinfo.assets[0]
        assert isinstance(asset, Asset)
        assert isinstance(asset.quantity, str)
        assert isinstance(asset.symbol, str)
        assert float(asset.quantity) 

    if len(accountinfo.positions) > 0:
        position = accountinfo.positions[0]
        assert isinstance(position, Position)
        assert isinstance(position.direction, str)
        assert isinstance(position.entryNotional, str)
        assert isinstance(position.markPrice, str)
        assert isinstance(position.notionalValue, str)
        assert isinstance(position.openPrice, str)
        assert isinstance(position.quantity, str)
        assert isinstance(position.symbol, str)
        assert isinstance(position.unrealizedFundingPnl, str)
        assert isinstance(position.unrealizedTradingPnl, str)
        
        # Check float values
        assert is_convertible_to_float(position.entryNotional)
        assert is_convertible_to_float(position.markPrice)
        assert is_convertible_to_float(position.notionalValue)
        assert is_convertible_to_float(position.openPrice)
        assert is_convertible_to_float(position.quantity)
        assert is_convertible_to_float(position.unrealizedFundingPnl)
        assert is_convertible_to_float(position.unrealizedTradingPnl)

    assert isinstance(accountinfo.balance, str)
    assert isinstance(accountinfo.maximalWithdraw, str)
    assert isinstance(accountinfo.numFreeTransfersRemaining, int)
    assert isinstance(accountinfo.totalOrderNotional, str)
    assert isinstance(accountinfo.totalPositionNotional, str)
    assert isinstance(accountinfo.totalUnrealizedFundingPnl, str)
    assert isinstance(accountinfo.totalUnrealizedPnl, str)
    assert isinstance(accountinfo.totalUnrealizedTradingPnl, str)
    assert isinstance(accountinfo.tradeMakerFeeRate, str)
    assert isinstance(accountinfo.tradeTakerFeeRate, str)

    # Check float values
    assert is_convertible_to_float(accountinfo.balance) 
    assert is_convertible_to_float(accountinfo.maximalWithdraw) 
    assert is_convertible_to_float(accountinfo.totalOrderNotional) 
    assert is_convertible_to_float(accountinfo.totalPositionNotional) 
    assert is_convertible_to_float(accountinfo.totalUnrealizedFundingPnl) 
    assert is_convertible_to_float(accountinfo.totalUnrealizedPnl) 
    assert is_convertible_to_float(accountinfo.totalUnrealizedTradingPnl) 

def test_get_account_trades():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    # assert account_id != "your-account-id"
    # assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)
    
    trades_response = client.get_account_trades()

    assert isinstance(trades_response, AccountTradesResponse)
    assert isinstance(trades_response.trades, list)

    for trade in trades_response.trades:
        assert isinstance(trade, AccountTrade)


def test_get_settlements_history():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert client != None
    # assert account_id != "your-account-id"
    # assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)

    settlements_response = client.get_settlements_history()

    assert isinstance(settlements_response, SettlementsResponse)
    assert isinstance(settlements_response.settlements, list)

    if len(settlements_response.settlements) > 0:
        settlement = settlements_response.settlements[0]
        assert isinstance(settlement, Settlement)
        assert isinstance(settlement.direction, str)
        assert isinstance(settlement.indexPrice, str)
        assert isinstance(settlement.quantity, str)
        assert isinstance(settlement.settledAmount, str)
        assert isinstance(settlement.symbol, str)
        assert isinstance(settlement.timestamp, int)

def test_get_pending_orders():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert client != None
    # assert account_id != "your-account-id"
    # assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)

    pending_orders_response = client.get_pending_orders()

    assert isinstance(pending_orders_response, PendingOrdersResponse)
    assert isinstance(pending_orders_response.orders, list)
    if len(pending_orders_response.orders) > 0:
        order = pending_orders_response.orders[0]
        assert isinstance(order, Order)
        assert isinstance(order.accountId, int)
        assert isinstance(order.availableQuantity, str)
        assert isinstance(order.contractId, int)
        assert isinstance(order.creationTime, int)
        assert isinstance(order.orderId, str)
        assert isinstance(order.orderType, OrderType)
        # assert isinstance(order.price, str) # in some cases the price is not returned
        assert isinstance(order.side, Side)
        assert isinstance(order.status, OrderStatus)
        assert isinstance(order.symbol, str)
        assert isinstance(order.totalQuantity, str)

def test_place_market_order():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key, private_key=private_key)
    assert client != None
    # assert account_id != "your-account-id"
    # assert api_key != "your-api-key"
    # assert private_key != "your-private"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)
    # client.set_private_key(private_key)

    # max_fees_percent is required for most actions related to orders, it must be at least as much as returned in the exchange_info
    max_fees_percent = 0.0005    
    
    # Market buy order OrderSide.BUY and OrderSide.BID are the same, both can be used
    # On a successful order placement the call returns the nonce and the order_id of the created order

    (nonce, order_id) = client.place_market_order("BTC/USDT-P", 0.0001, Side.BUY, max_fees_percent)
    # Market sell order OrderSide.SELL and OrderSide.ASK are the same, both can be used
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
    client.get_order_details(order_id=order_id)
    client.get_order_details(nonce=nonce)

    # Get current price of the market
    prices = client.get_prices("BTC/USDT-P")   

    # Limit orders can be placed similarly to market orders
    (nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, float(prices.markPrice), Side.BUY, max_fees_percent)
    (nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, float(prices.markPrice), Side.SELL, max_fees_percent)
    (nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, float(prices.markPrice), Side.BID, max_fees_percent, creation_deadline=2)
    (nonce, order_id) = client.place_limit_order("BTC/USDT-P", 0.0001, float(prices.markPrice), Side.ASK, max_fees_percent, trigger_price=float(prices.markPrice)*1.05)

    # Pending or partially filled orders can be updated using the order_id
    # Quantity, price and trigger price can be updated separately or any number of them at once
    # The single order update request is convenient, but does two requests behind the curtains
    # First it will downlowd the order details of the order to be updated to get all data to create a correct signature
    client.get_order_details(order_id=order_id)

    client.update_order(order_id, max_fees_percent, quantity=0.002)
    client.get_order_details(order_id=order_id)
    client.update_order(order_id, max_fees_percent, price=float(prices.markPrice)*1.025)
    client.get_order_details(order_id=order_id)

    client.update_order(order_id, max_fees_percent, trigger_price=float(prices.markPrice)*1.05)
    client.get_order_details(order_id=order_id)

    client.update_order(order_id, max_fees_percent, quantity=0.001, price=float(prices.markPrice)*1.075, trigger_price=float(prices.markPrice)*1.08)
    client.get_order_details(order_id=order_id)

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

def test_get_capital_balance():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert client != None
    assert account_id != "your-account-id"
    assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)

    capitalresult = client.get_capital_balance()
    print_data(capitalresult)
    assert isinstance(capitalresult, CapitalBalance)
    assert isinstance(capitalresult.balance, str)

def test_get_capital_history():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert client != None
    assert account_id != "your-account-id"
    assert api_key != "your-api-key"
    # client.set_account_id(account_id)
    # client.set_api_key(api_key)

    history = client.get_capital_history()
    
    assert isinstance(history, CapitalHistory)
    assert isinstance(history.transactions, list)
    
    for tx in history.transactions:
        assert isinstance(tx, Transaction)
 

def test_withdraw():
    client = HibachiApiClient(api_endpoint, data_api_endpoint)
    assert client != None
    assert account_id != "your-account-id"
    assert api_key != "your-api-key"
    assert private_key != "your-private"
    client.set_account_id(account_id)
    client.set_api_key(api_key)
    client.set_private_key(private_key)

    # Get exchange info to get fees
    exchange_info = client.get_exchange_info()
    withdrawal_fees = exchange_info.feeConfig.withdrawalFees

    # Test withdraw request
    try:
        response = client.withdraw(
            coin="USDT",
            withdraw_address="0x0000000000000000000000000000000000000000",
            quantity="1.0",
            max_fees=withdrawal_fees
        )
        assert isinstance(response, WithdrawResponse)
        assert isinstance(response.orderId, str)
    except HibachiApiError as e:
        # Withdrawal may fail if insufficient balance
        assert e.status_code in [400, 403, 409]

def test_get_deposit_info():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key)
    assert client != None
    
    # To get public_key inspect network traffic in the browser.
    # GET api.hibachi.xyz/user/subaccounts
    # or 
    # GET api-test.hibachi.xyz/capital/deposit-info

    deposit_info = client.get_deposit_info(public_key)    
    print_data(deposit_info)
    assert isinstance(deposit_info, DepositInfo)
    assert isinstance(deposit_info.depositAddressEvm, str)
    assert deposit_info.depositAddressEvm.startswith("0x")
    assert len(deposit_info.depositAddressEvm) == 42  # Valid Ethereum address length

def test_get_inventory():
    client = HibachiApiClient()
    assert client != None

    inventory = client.get_inventory()
    print_data(inventory)

    assert isinstance(inventory, InventoryResponse)    
    assert isinstance(inventory.crossChainAssets, list)
  
    for cca in inventory.crossChainAssets:
        assert isinstance(cca, CrossChainAsset)

    assert isinstance(inventory.feeConfig, FeeConfig)
    assert isinstance(inventory.markets, list)

    for market in inventory.markets:
        assert isinstance(market, Market)

    assert isinstance(inventory.tradingTiers, list)

    for tradingTier in inventory.tradingTiers:
        assert isinstance(tradingTier, TradingTier)


def test_transfer():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key, private_key=private_key)
    assert client != None

    transfer = client.transfer(
        coin="USDT",
        quantity="5",
        dstPublicKey="0x049c8f81dd7c8001a400a9dd7df7a28ac4a11dd91a6f8ec9ee2c94cf6083116da034f8cd466799f65b11e3416aab95166b8d9e403ec2f268c93cbe150e50500b", 
        max_fees="0")

    assert transfer.status == "success"

def test_cancel_order():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key, private_key=private_key)
    assert client != None
    start_order_count = len(client.get_pending_orders().orders)

    current_price = client.get_prices("BTC/USDT-P")
    print(f"current_price: {current_price}")

    (nonce, order_id) = client.place_limit_order(
        symbol="BTC/USDT-P", 
        quantity=0.0001, 
        side=Side.ASK, 
        max_fees_percent=0.005, 
        price=float(current_price.askPrice) *1.05
    )
    assert len(client.get_pending_orders().orders) == start_order_count + 1
    cancel_result = client.cancel_order(order_id=order_id, nonce=nonce)
    assert len(client.get_pending_orders().orders) == start_order_count

    (nonce, order_id) = client.place_limit_order(
        symbol="BTC/USDT-P", 
        quantity=0.0001, 
        side=Side.ASK, 
        max_fees_percent=0.005, 
        price=float(current_price.askPrice) *1.05
    )
    assert len(client.get_pending_orders().orders) == start_order_count + 1
    cancel_result = client.cancel_order(order_id=order_id)
    assert len(client.get_pending_orders().orders) == start_order_count

    (nonce, order_id) = client.place_limit_order(
        symbol="BTC/USDT-P", 
        quantity=0.0001, 
        side=Side.ASK, 
        max_fees_percent=0.005, 
        price=float(current_price.askPrice) *1.05
    )
    assert len(client.get_pending_orders().orders) == start_order_count + 1
    cancel_result = client.cancel_order(nonce=nonce)
    assert len(client.get_pending_orders().orders) == start_order_count

    print(f"orders count: {len(client.get_pending_orders().orders)}")

    for order in client.get_pending_orders().orders:
        print(f"order: {order}")
        # delete order
        print(f"deleting order: {order.orderId}")
        client.cancel_order(order_id=int(order.orderId)) 

def test_cancel_all_orders():
    client = HibachiApiClient(api_endpoint, data_api_endpoint, account_id=account_id, api_key=api_key, private_key=private_key)
    assert client != None

    current_price = client.get_prices("BTC/USDT-P")
    print(f"current_price: {current_price}")

    start_order_count = len(client.get_pending_orders().orders)

    (nonce, order_id) = client.place_limit_order(
        symbol="BTC/USDT-P", 
        quantity=0.0001, 
        side=Side.ASK, 
        max_fees_percent=0.005, 
        price=float(current_price.askPrice) *1.05
    )

    assert nonce != None
    assert order_id != None

    after_adding_order_count = len(client.get_pending_orders().orders)

    assert after_adding_order_count == start_order_count + 1

    print(f"after_adding_order_count: {after_adding_order_count}")

    cancel_result = client.cancel_all_orders()
    print_data(cancel_result)

    order_count_after_cancel_all = len(client.get_pending_orders().orders)

    print(f"order_count_after_cancel_all: {order_count_after_cancel_all}")

    assert order_count_after_cancel_all == 0
