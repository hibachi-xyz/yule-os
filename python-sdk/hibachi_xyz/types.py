from typing import List, Tuple, Optional, Dict, Any, TypedDict, Union, TypeAlias
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Interval(Enum):
    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"

Nonce: TypeAlias = int
OrderId: TypeAlias = int

class HibachiApiError(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class TWAPQuantityMode(Enum):
    FIXED = "FIXED"
    RANDOM = "RANDOM"

class TWAPConfig:
    duration_minutes: int
    quantity_mode: TWAPQuantityMode

    def __init__(self, duration_minutes: int, quantity_mode: TWAPQuantityMode):
        self.duration_minutes = duration_minutes
        self.quantity_mode = quantity_mode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "twapDurationMinutes": self.duration_minutes,
            "twapQuantityMode": self.quantity_mode.value
        }

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    # SCHEDULED_TWAP = "SCHEDULED_TWAP"

class Side(Enum):
    BID = "BID"
    ASK = "ASK"
    SELL = "SELL"
    BUY = "BUY"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    SCHEDULED_TWAP = "SCHEDULED_TWAP"
    PLACED = "PLACED"

@dataclass
class Order:
    accountId: int
    availableQuantity: str
    contractId: Optional[int]
    creationTime: Optional[int]
    finishTime: Optional[int]
    numOrdersRemaining: Optional[int]
    numOrdersTotal: Optional[int]
    orderId: str
    orderType: OrderType
    price: Optional[str]
    quantityMode: Optional[str]
    side: Side
    status: OrderStatus
    symbol: str
    totalQuantity: Optional[str]
    triggerPrice: Optional[str]

    def __init__(self, 
                 accountId: int, 
                 availableQuantity: str, 
                 orderId: str,
                 orderType: str, 
                 side: str, 
                 status: str,
                 symbol: str,  
                 numOrdersRemaining: Optional[int] = None,
                 numOrdersTotal: Optional[int] = None, 
                 quantityMode: Optional[str] = None,
                 finishTime: Optional[int] = None,
                 price: Optional[str] = None, 
                 totalQuantity: Optional[str] = None,
                 creationTime: Optional[int] = None,
                 contractId: Optional[int] = None,
                 triggerPrice: Optional[str] = None):
        self.accountId = accountId
        self.availableQuantity = availableQuantity
        self.contractId = contractId
        self.creationTime = creationTime
        self.finishTime = finishTime
        self.numOrdersRemaining = numOrdersRemaining
        self.numOrdersTotal = numOrdersTotal
        self.orderId = orderId
        self.orderType = OrderType(orderType)
        self.price = price
        self.quantityMode = quantityMode
        self.side = Side(side)
        self.status = OrderStatus(status)
        self.symbol = symbol
        self.totalQuantity = totalQuantity
        self.triggerPrice = triggerPrice



@dataclass
class FeeConfig:
    depositFees: str
    instantWithdrawDstPublicKey: str
    instantWithdrawalFees: List[List[Union[int, float]]]
    tradeMakerFeeRate: str
    tradeTakerFeeRate: str
    transferFeeRate: str
    withdrawalFees: str

@dataclass
class FutureContract:
    displayName: str
    id: int
    maintenanceFactorForPositions: str
    marketCloseTimestamp: Optional[str]
    marketOpenTimestamp: Optional[str]
    minNotional: str
    minOrderSize: str
    orderbookGranularities: List[str]
    riskFactorForOrders: str
    riskFactorForPositions: str
    settlementDecimals: int
    settlementSymbol: str
    status: str
    stepSize: str
    symbol: str
    tickSize: str
    underlyingDecimals: int
    underlyingSymbol: str

@dataclass
class WithdrawalLimit:
    lowerLimit: str
    upperLimit: str

@dataclass
class MaintenanceWindow:
    begin: float
    end: float
    note: str

@dataclass
class ExchangeInfo:
    feeConfig: FeeConfig
    futureContracts: List[FutureContract]
    instantWithdrawalLimit: WithdrawalLimit
    maintenanceWindow: List[MaintenanceWindow]
    # can be NORMAL, MAINTENANCE
    status: str

@dataclass
class FundingRateEstimation:
    estimatedFundingRate: str
    nextFundingTimestamp: int

@dataclass
class PriceResponse:
    askPrice: str
    bidPrice: str
    fundingRateEstimation: FundingRateEstimation
    markPrice: str
    spotPrice: str
    symbol: str
    tradePrice: str

@dataclass
class StatsResponse:
    high24h: str
    low24h: str
    symbol: str
    volume24h: str

class TakerSide(Enum):
    Buy = "Buy"
    Sell = "Sell"

@dataclass
class Trade:
    price: str
    quantity: str
    takerSide: TakerSide
    timestamp: int

@dataclass
class TradesResponse:
    trades: List[Trade]

@dataclass
class Kline:
    close: str
    high: str
    low: str
    open: str
    interval: str
    timestamp: int
    volumeNotional: str

@dataclass
class KlinesResponse:
    klines: List[Kline]

@dataclass
class OpenInterestResponse:
    totalQuantity: str

@dataclass
class OrderBookLevel:
    price: str
    quantity: str

@dataclass
class OrderBook:
    ask: List[OrderBookLevel]
    bid: List[OrderBookLevel]

@dataclass
class Asset:
    quantity: str
    symbol: str

@dataclass
class Position:
    direction: str
    entryNotional: str
    markPrice: str
    notionalValue: str
    openPrice: str
    quantity: str
    symbol: str
    unrealizedFundingPnl: str
    unrealizedTradingPnl: str

@dataclass
class AccountInfo:
    assets: List[Asset]
    balance: str
    maximalWithdraw: str
    numFreeTransfersRemaining: int
    positions: List[Position]
    totalOrderNotional: str
    totalPositionNotional: str
    totalUnrealizedFundingPnl: str
    totalUnrealizedPnl: str
    totalUnrealizedTradingPnl: str
    tradeMakerFeeRate: str
    tradeTakerFeeRate: str

@dataclass
class AccountTrade:
    askAccountId: int
    askOrderId: int
    bidAccountId: int
    bidOrderId: int
    fee: str
    id: int
    orderType: str
    price: str
    quantity: str
    realizedPnl: str
    side: str
    symbol: str
    timestamp: int

@dataclass
class AccountTradesResponse:
    trades: List[AccountTrade]

@dataclass
class Settlement:
    direction: str
    indexPrice: str
    quantity: str
    settledAmount: str
    symbol: str
    timestamp: int

@dataclass
class SettlementsResponse:
    settlements: List[Settlement]




@dataclass
class PendingOrdersResponse:
    orders: List[Order]

@dataclass
class CapitalBalance:
    balance: str

@dataclass
class Transaction:
    id: int
    assetId: int
    quantity: str
    status: str
    timestamp: int
    transactionType: str
    transactionHash: Optional[Union[str,str]]
    token: Optional[str]
    etaTsSec: Optional[int]
    blockNumber: Optional[int]
    chain: Optional[str]
    instantWithdrawalChain: Optional[str]
    instantWithdrawalToken: Optional[str]
    isInstantWithdrawal: Optional[bool]
    withdrawalAddress: Optional[str]
    receivingAccountId: Optional[int]
    receivingAddress: Optional[str]
    srcAccountId: Optional[int]
    srcAddress: Optional[str]

    def __init__(self, 
                    id: int,
                    assetId: int,
                    quantity: str,
                    status: str,
                    timestamp: int,
                    transactionType: str,
                    transactionHash: Optional[Union[str,str]] = None,
                    token: Optional[str] = None,
                    etaTsSec: Optional[int] = None,
                    blockNumber: Optional[int] = None,
                    chain: Optional[str] = None,
                    instantWithdrawalChain: Optional[str] = None,
                    instantWithdrawalToken: Optional[str] = None,
                    isInstantWithdrawal: Optional[bool] = None,
                    withdrawalAddress: Optional[str] = None,
                    receivingAddress: Optional[str] = None,
                    receivingAccountId: Optional[int] = None,
                    srcAccountId: Optional[int] = None,
                    srcAddress: Optional[str] = None):
        self.id = id
        self.assetId = assetId
        self.quantity = quantity
        self.status = status
        self.timestamp = timestamp
        self.transactionType = transactionType
        self.transactionHash = transactionHash
        self.token = token
        self.etaTsSec = etaTsSec
        self.blockNumber = blockNumber
        self.chain = chain
        self.instantWithdrawalChain = instantWithdrawalChain
        self.instantWithdrawalToken = instantWithdrawalToken
        self.isInstantWithdrawal = isInstantWithdrawal
        self.withdrawalAddress = withdrawalAddress
        self.receivingAddress = receivingAddress
        self.receivingAccountId = receivingAccountId
        self.srcAccountId = srcAccountId
        self.srcAddress = srcAddress
@dataclass
class CapitalHistory:
    transactions: List[Transaction]

@dataclass
class WithdrawRequest:
    accountId: int
    coin: str
    withdrawAddress: str
    network: str
    quantity: str
    maxFees: str
    signature: str

@dataclass
class WithdrawResponse:
    orderId: str

@dataclass
class TransferRequest:
    accountId: int
    coin: str
    fees: str
    nonce: int
    quantity: str
    dstPublicKey: str
    signature: str

@dataclass
class TransferResponse:
    status: str

@dataclass
class DepositInfo:
    depositAddressEvm: str

class WebSocketSubscriptionTopic(Enum):
    MARK_PRICE = "mark_price"
    SPOT_PRICE = "spot_price"
    FUNDING_RATE_ESTIMATION = "funding_rate_estimation"
    TRADES = "trades"
    KLINES = "klines"
    ORDERBOOK = "orderbook"
    ASK_BID_PRICE ="ask_bid_price"
    

@dataclass
class WebSocketSubscription:
    symbol: str
    topic: WebSocketSubscriptionTopic

@dataclass
class WebSocketMarketSubscriptionListResponse:
    subscriptions: List[WebSocketSubscription]

#AUTOGEN BELOW

@dataclass
class WebSocketResponse:
    id: Optional[int]
    result: Optional[Dict[str, Any]]
    status: Optional[int]
    subscriptions: Optional[List[WebSocketSubscription]]

@dataclass
class WebSocketEvent:
    account: str
    event: str
    data: Dict[str, Any]

@dataclass
class WebSocketOrderCancelParams:
    orderId: str
    accountId: str
    nonce: int

@dataclass
class WebSocketOrderModifyParams:
    orderId: str
    accountId: str
    symbol: str
    quantity: str
    price: str
    maxFeesPercent: str

@dataclass
class WebSocketOrderStatusParams:
    orderId: str
    accountId: str

@dataclass
class WebSocketOrdersStatusParams:
    accountId: str

@dataclass
class WebSocketOrdersCancelParams:
    accountId: str
    nonce: str
    contractId: Optional[int] = None

@dataclass
class WebSocketBatchOrder:
    action: str
    nonce: int
    symbol: str
    orderType: str
    side: str
    quantity: str
    price: str
    maxFeesPercent: str
    signature: str
    orderId: Optional[str] = None
    updatedQuantity: Optional[str] = None
    updatedPrice: Optional[str] = None

@dataclass
class WebSocketOrdersBatchParams:
    accountId: str
    orders: List[WebSocketBatchOrder]

@dataclass
class WebSocketStreamStartParams:
    accountId: str

@dataclass
class WebSocketStreamPingParams:
    accountId: str
    listenKey: str
    timestamp: int

@dataclass
class WebSocketStreamStopParams:
    accountId: str
    listenKey: str
    timestamp: int

@dataclass
class AccountSnapshot:
    account_id: int
    balance: str
    positions: List[Position]

@dataclass
class AccountStreamStartResult:
    accountSnapshot: AccountSnapshot
    listenKey: str



@dataclass
class OrderPlaceParams:
    symbol: str
    quantity: float
    side: Side
    orderType: OrderType
    price: Optional[str]
    trigger_price: Optional[float]
    twap_config: Optional[TWAPConfig]
    maxFeesPercent: float
    orderFlags: Optional[str] = None
    creation_deadline: Optional[int] = None

@dataclass
class OrderCancelParams:
    orderId: str
    accountId: str
    nonce: int

@dataclass
class OrderModifyParams:
    orderId: str
    accountId: int
    symbol: str
    quantity: str
    price: str
    side: Side
    maxFeesPercent: str
    nonce: Optional[int]

@dataclass
class OrderStatusParams:
    orderId: str
    accountId: str

@dataclass
class OrdersStatusParams:
    accountId: int

@dataclass
class OrdersCancelParams:
    accountId: str
    nonce: str
    contractId: Optional[int] = None

@dataclass
class BatchOrder:
    action: str
    nonce: int
    symbol: Optional[str] = None
    orderType: Optional[OrderType] = None
    side: Optional[Side] = None
    quantity: Optional[str] = None
    price: Optional[str] = None
    maxFeesPercent: Optional[str] = None
    orderId: Optional[str] = None
    updatedQuantity: Optional[str] = None
    updatedPrice: Optional[str] = None
    signature: Optional[str] = None

@dataclass
class OrdersBatchParams:
    accountId: str
    orders: List[BatchOrder]

@dataclass
class EnableCancelOnDisconnectParams:
    nonce: int

@dataclass
class OrderResponse:
    accountId: str
    availableQuantity: str
    orderId: str
    orderType: OrderType
    price: str
    side: Side
    status: OrderStatus
    symbol: str
    totalQuantity: str


@dataclass
class OrderPlaceResponseResult:
    orderId: str

@dataclass
class OrderPlaceResponse:
    id:int
    result: OrderPlaceResponseResult
    status: int

@dataclass
class OrdersStatusResponse:
    id: int
    result: List[Order]
    status: Optional[int]

@dataclass
class OrderStatusResponse:
    id: int
    result: Order
    status: Optional[int]



@dataclass
class CrossChainAsset:
    chain: str
    exchangeRateFromUSDT: str
    exchangeRateToUSDT: str
    instantWithdrawalLowerLimitInUSDT: str
    instantWithdrawalUpperLimitInUSDT: str
    token: str



@dataclass
class TradingTier:
    level: int
    lowerThreshold: str
    title: str
    upperThreshold: str



@dataclass
class MarketInfo:
    category: str
    markPrice: str
    price24hAgo: str
    priceLatest: str
    tags: List[str]

@dataclass 
class Market:
    contract: FutureContract
    info: MarketInfo

@dataclass
class InventoryResponse:
    crossChainAssets: List[CrossChainAsset]
    feeConfig: FeeConfig
    markets: List[Market]
    tradingTiers: List[TradingTier]