import asyncio
import os
from hibachi_xyz import HibachiWSAccountClient,WebSocketSubscription,WebSocketSubscriptionTopic,print_data
from dotenv import load_dotenv

async def example_ws_account():

    # load environment variables from .env file
    # make sure to create a .env file with the required variables
    # or set them in your environment
    load_dotenv()
    
    
    myaccount_live = HibachiWSAccountClient(
        api_endpoint=os.environ.get('HIBACHI_API_ENDPOINT').replace("https://", "wss://"),
        api_key = os.environ.get('HIBACHI_API_KEY'), 
        account_id = os.environ.get('HIBACHI_ACCOUNT_ID')
    )

    await myaccount_live.connect()
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
    

    print("Listening:")
    # Listening:
    # ping...
    # pong!
    # None

    counter = 0
    while counter < 1:
        message = await myaccount_live.listen()
        print_data(message)
        counter += 1  

if __name__ == "__main__":
    # This code only runs when the file is executed directly
    asyncio.run(example_ws_account())