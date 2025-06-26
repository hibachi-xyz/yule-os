import asyncio
import os

from hibachi_xyz import (HibachiWSAccountClient, WebSocketSubscription,
                         WebSocketSubscriptionTopic, print_data)
from hibachi_xyz.env_setup import setup_environment


async def example_ws_account():

    # load environment variables from .env file
    # make sure to create a .env file with the required variables
    # or set them in your environment
    api_endpoint, data_api_endpoint, api_key, account_id, _, _, _ = setup_environment()

    
    myaccount_live = HibachiWSAccountClient(
        api_endpoint=api_endpoint.replace("https://", "wss://"),
        api_key = api_key,
        account_id = account_id
    )

    # await myaccount_live.connect()
    # result_start = await myaccount_live.stream_start()
    
    try:
        # Connect to the WebSocket
        await myaccount_live.connect()

        # Start the stream
        result_start = await myaccount_live.stream_start()
        print_data(result_start)
        # {
        #     'accountSnapshot': {
        #         'account_id': 273,
        #         'balance': '341.600700',
        #         'positions': [
        #             {
        #                 'direction': 'Long',
        #                 'entryNotional': '290.181588',
        #                 'markPrice': '143.4090474',
        #                 'notionalValue': '286.818094',
        #                 'openPrice': '145.0907940',
        #                 'quantity': '2.00000000',
        #                 'symbol': 'SOL/USDT-P',
        #                 'unrealizedFundingPnl': '-0.040593',
        #                 'unrealizedTradingPnl': '-3.363493'
        #             },
        #             {
        #                 'direction': 'Long',
        #                 'entryNotional': '16635.158909',
        #                 'markPrice': '107229.48789',
        #                 'notionalValue': '16599.124725',
        #                 'openPrice': '107462.26685',
        #                 'quantity': '0.1548000000',
        #                 'symbol': 'BTC/USDT-P',
        #                 'unrealizedFundingPnl': '0.000000',
        #                 'unrealizedTradingPnl': '-36.034183'
        #             }
        #         ]
        #     },
        #     'listenKey': '273-dnqbex2pvgaogsb6akyxp4mp65cu7hkxlq'
        # }
    

        # Listening for messages from the WebSocket
        print("Listening:")
        # Listening:
        # ping...
        # pong!
        # None
        counter = 0
        while counter < 10:  # You can adjust the number of messages to listen to
            message = await myaccount_live.listen()
            if message is None:
                print("Connection closed or lost.")
                break
            print_data(message)
            counter += 1

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up and close the WebSocket connection
        print("Closing connection.")
        await myaccount_live.disconnect()

    print_data(result_start)
    

if __name__ == "__main__":
    # This code only runs when the file is executed directly
    asyncio.run(example_ws_account())