import asyncio
from dataclasses import asdict
import json
import websockets
from typing import List, Dict, Callable

from .types import (
    WebSocketMarketSubscriptionListResponse,
    WebSocketSubscription,
    WebSocketSubscriptionTopic,
)

from .helpers import print_data, connect_with_retry, default_data_api_url

class HibachiWSMarketClient:
    """
    Market Websocket Client is used to subscribe to market data like mark price, spot price, funding rate, trades, candle sticks, orderbook, ask/bid prices.

    ## Example usage:

    ```python
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
    ```

    """
    def __init__(self, api_endpoint: str = default_data_api_url):
        self.api_endpoint = api_endpoint.replace("https://", "wss://") + "/ws/market"
        self.websocket = None
        self.message_id = 0
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._response_handlers: Dict[int, Callable] = {}

    async def connect(self):
        """Establish WebSocket connection with retry logic"""
        self.websocket = await connect_with_retry(self.api_endpoint)
        return self

    async def list_subscriptions(self) -> WebSocketMarketSubscriptionListResponse:
        """List market subscriptions that are currently active"""
        await self.websocket.send(json.dumps({
            "method": "list_subscriptions"
        }))
        response_data: Dict[str, any] = {}
        max_packets = 10
        counter = 0

        while response_data.get("subscriptions") is None and counter < max_packets:
            counter += 1    
            response = await self.websocket.recv()
            response_data = json.loads(response)  

        if response_data.get("subscriptions") is not None:
            response_data["subscriptions"] = [WebSocketSubscription(**{**sub, "topic": WebSocketSubscriptionTopic(sub["topic"])}) for sub in response_data["subscriptions"]]
            return WebSocketMarketSubscriptionListResponse(**response_data)
        
        raise ValueError(f"Could not list subscriptions.")

    async def subscribe(self, subscriptions: List[WebSocketSubscription]) -> bool:  
        """
        Create new market subscriptions.
        """      
        await self.websocket.send(json.dumps({
            "method": "subscribe",
            "parameters": {
                "subscriptions": [{**asdict(sub), "topic": sub.topic.value} for sub in subscriptions]
            }
        }))
        return await self.websocket.recv()
    
    async def unsubscribe(self, subscriptions: List[WebSocketSubscription]) -> bool:
        """
        Unsubscribe from specific market subscriptions
        """
        packet = json.dumps({
            "method": "unsubscribe",
            "parameters": {
                "subscriptions": [{**asdict(sub), "topic": sub.topic.value} for sub in subscriptions]
            }
        })
        await self.websocket.send(packet)
        return True
