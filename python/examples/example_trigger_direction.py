"""Example demonstrating trigger_direction support in place_market_order and place_limit_order.

Run against the test environment:
    ENVIRONMENT=test python examples/example_trigger_direction.py

What this tests:
  1. place_market_order with trigger_price + trigger_direction=LOW  (stop-loss trigger)
  2. place_limit_order  with trigger_price + trigger_direction=HIGH (take-profit trigger)
  3. SDK guard: trigger_price + tpsl together raises ValidationError immediately
  4. SDK guard: trigger_direction without trigger_price places a plain market order

Orders placed in (1) and (2) are cancelled immediately after placement to avoid
leaving resting orders on the book.
"""

from hibachi_xyz import HibachiApiClient, print_data, round_price_to_tick
from hibachi_xyz.env_setup import setup_environment
from hibachi_xyz.errors import ValidationError
from hibachi_xyz.types import OrderFlags, Side, TPSLConfig, TriggerDirection

SYMBOL = "BTC/USDT-P"
QUANTITY = 0.0001


def example_trigger_direction():
    api_endpoint, data_api_endpoint, api_key, account_id, private_key, _, _ = (
        setup_environment()
    )

    client = HibachiApiClient(
        api_url=api_endpoint,
        data_api_url=data_api_endpoint,
        api_key=api_key,
        account_id=account_id,
        private_key=private_key,
    )

    prices = client.get_prices(SYMBOL)
    exch_info = client.get_exchange_info()
    tick = client.get_tick_size(SYMBOL)
    mark = float(prices.markPrice)
    max_fees = float(exch_info.feeConfig.tradeTakerFeeRate) * 2.0

    print(f"Mark price: {mark}")

    # --- Test 1: market order with trigger_price + trigger_direction=LOW ---
    # Simulates a stop-loss trigger: fires when price falls below trigger.
    stop_price = round_price_to_tick(mark * 0.90, tick)
    print(
        f"\n[1] place_market_order  trigger_price={stop_price}  trigger_direction=LOW"
    )
    nonce, order_id = client.place_market_order(
        symbol=SYMBOL,
        quantity=QUANTITY,
        side=Side.ASK,
        max_fees_percent=max_fees,
        trigger_price=stop_price,
        trigger_direction=TriggerDirection.LOW,
        order_flags=OrderFlags.ReduceOnly,
    )
    print(f"    Placed order_id={order_id}  nonce={nonce}")
    print_data(client.get_order_details(order_id))
    client.cancel_order(order_id, max_fees)
    print(f"    Cancelled order_id={order_id}")

    # --- Test 2: limit order with trigger_price + trigger_direction=HIGH ---
    # Simulates a take-profit trigger: fires when price rises above trigger.
    tp_trigger = round_price_to_tick(mark * 1.10, tick)
    tp_limit = round_price_to_tick(mark * 1.11, tick)
    print(
        f"\n[2] place_limit_order  price={tp_limit}  trigger_price={tp_trigger}  trigger_direction=HIGH"
    )
    nonce, order_id = client.place_limit_order(
        symbol=SYMBOL,
        quantity=QUANTITY,
        price=tp_limit,
        side=Side.ASK,
        max_fees_percent=max_fees,
        trigger_price=tp_trigger,
        trigger_direction=TriggerDirection.HIGH,
        order_flags=OrderFlags.ReduceOnly,
    )
    print(f"    Placed order_id={order_id}  nonce={nonce}")
    print_data(client.get_order_details(order_id))
    client.cancel_order(order_id, max_fees)
    print(f"    Cancelled order_id={order_id}")

    # --- Test 3: SDK guard — trigger_price + tpsl must raise ValidationError ---
    print("\n[3] SDK guard: trigger_price + tpsl should raise ValidationError")
    raised = False
    try:
        client.place_market_order(
            symbol=SYMBOL,
            quantity=QUANTITY,
            side=Side.BID,
            max_fees_percent=max_fees,
            trigger_price=stop_price,
            tpsl=TPSLConfig().add_take_profit(price=tp_trigger),
        )
    except ValidationError as e:
        raised = True
        print(f"    OK: ValidationError raised as expected — {e}")
    assert raised, "Expected ValidationError for trigger_price + tpsl combination"

    # --- Test 4: trigger_direction without trigger_price places a plain market order ---
    # trigger_direction is only serialised when trigger_price is also set,
    # so passing it alone should place a plain market order without error.
    print(
        "\n[4] trigger_direction without trigger_price — should place a plain market order"
    )
    nonce, order_id = client.place_market_order(
        symbol=SYMBOL,
        quantity=QUANTITY,
        side=Side.BID,
        max_fees_percent=max_fees,
        trigger_direction=TriggerDirection.HIGH,
    )
    print(f"    Placed order_id={order_id}  nonce={nonce}")
    print_data(client.get_order_details(order_id))

    print("\nAll checks passed.")


if __name__ == "__main__":
    example_trigger_direction()
