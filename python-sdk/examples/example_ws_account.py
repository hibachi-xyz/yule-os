import asyncio
import os
import time
from datetime import datetime, timezone

from hibachi_xyz import HibachiWSAccountClient, print_data
from hibachi_xyz.env_setup import setup_environment


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

async def example_ws_account():
    print("Loading environment variables from .env file")
    api_endpoint, _, api_key, account_id, _, _, _ = setup_environment()
    ws_base_url = api_endpoint.replace("https://", "wss://")

    attempt = 1
    backoff = 1  # seconds

    while True:
        print(f"[{now()}] [Attempt {attempt}] Connecting to WebSocket...")
        myaccount_live = HibachiWSAccountClient(
            api_endpoint=ws_base_url,
            api_key=api_key,
            account_id=account_id
        )

        start_time = time.time()
        try:
            await myaccount_live.connect()
            result_start = await myaccount_live.stream_start()
            print(f"[Connected] stream_start result:")
            print_data(result_start)

            print("Listening for account WebSocket messages (Ctrl+C to stop)...")
            last_msg_time = time.time()

            while True:
                message = await myaccount_live.listen()
                if message is None:
                    print(f"[{now()}] No message received. (Ping sent.) "
                          f"Last message was {int(time.time() - last_msg_time)}s ago.")
                    continue
                last_msg_time = time.time()
                print_data(message)

        except asyncio.CancelledError:
            print(f"[{now()}] CancelledError caught. Cleaning up WebSocket connection.")
            await myaccount_live.disconnect()
            break

        except Exception as e:
            print(f"[Error] {e}")

        finally:
            duration = time.time() - start_time
            print(f"[{now()}] Disconnected. Connection lasted {duration:.2f} seconds.")
            await myaccount_live.disconnect()
            print(f"[{now()}] Client cleaned up.")

        print(f"Reconnecting in {backoff} seconds...\n")
        try:
            await asyncio.sleep(backoff)
        except asyncio.CancelledError:
            print(f"[{now()}] Cancelled during backoff sleep. Exiting.")
            break

        attempt += 1
        backoff = min(backoff * 2, 60)

if __name__ == "__main__":
    try:
        asyncio.run(example_ws_account())
    except KeyboardInterrupt:
        print(f"[{now()}] KeyboardInterrupt received. Exiting cleanly.")
