import asyncio
from dataclasses import asdict
import json
import websockets
from typing import List, Optional, Dict, Any, Callable
from eth_keys import keys

from .types import (
    AccountInfo,
    AccountSnapshot,
    AccountTradesResponse,
    Position,
    SettlementsResponse,
    PendingOrdersResponse,
    CapitalBalance,
    CapitalHistory,
    AccountStreamStartResult,
    WithdrawRequest,
    WithdrawResponse,
    DepositInfo
)

from hibachi_xyz.helpers import print_data, connect_with_retry, default_api_url


class HibachiWSAccountClient:
    """
    Account Websocket Client is used to subscribe to account balance and positions.

    ```python
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
    ```

    """
    def __init__(self, api_key: str, account_id: str, api_endpoint: str = default_api_url):
        self.api_endpoint = api_endpoint.replace("https://", "wss://") + "/ws/account"
        self.websocket = None
        self.message_id = 0
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._response_handlers: Dict[int, Callable] = {}
        self.api_key = api_key
        self.account_id = account_id
        self.listenKey: str | None = None

    async def connect(self):
        """Establish WebSocket connection with retry logic"""
        self.websocket = await connect_with_retry(
            web_url=self.api_endpoint + f"?accountId={self.account_id}", 
            headers=[("Authorization", self.api_key)]
        )
        return self


    async def stream_start(self) -> AccountStreamStartResult:
        """Get account information including assets, positions, and balances"""
        self.message_id += 1
        message = {
            "id": self.message_id,
            "method": "stream.start",
            "params": {
                "accountId": self.account_id
            }
        }
        
        await self.websocket.send(json.dumps(message))
        
        response = await self.websocket.recv()
        response_data = json.loads(response)
        result = AccountStreamStartResult(**response_data["result"])
        result.accountSnapshot = AccountSnapshot(**response_data["result"]["accountSnapshot"])
        result.accountSnapshot.positions = [Position(**pos) for pos in response_data["result"]["accountSnapshot"]["positions"]]    
        self.listenKey = result.listenKey
        return result
    
    async def listen(self) -> AccountStreamStartResult:
        """Listen for messages with a 5-second timeout that triggers a ping"""
        try:
            # Set a 5-second timeout for receiving messages
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            if response_data.get("result") is None:
                # posible response to a ping packet...
                raise ValueError(f"Unexpected response: {response_data}")
            result = AccountStreamStartResult(**response_data["result"])
            result.accountSnapshot = AccountSnapshot(**response_data["result"]["accountSnapshot"])
            result.accountSnapshot.positions = [Position(**pos) for pos in response_data["result"]["accountSnapshot"]["positions"]]
            return result
        except asyncio.TimeoutError:
            # If timeout occurs, send a ping and then continue listening
            await self.ping()
            # Recursively call listen again to wait for a response
            return None
    
    async def ping(self):

        if self.listenKey is None:
            raise ValueError("listenKey is not set. Call stream_start() first.")

        self.message_id += 1
        message = {
            "id": self.message_id,
            "method": "stream.ping",
            "params": {
                "accountId": self.account_id,
                "listenKey": self.listenKey
            }
        }
        
        print("ping...")
        await self.websocket.send(json.dumps(message))

        
        response = await self.websocket.recv() # Wait for the pong response
        parsed = json.loads(response)
        if parsed.get("status") == 200:
            print("pong!")

    async def disconnect(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None


   