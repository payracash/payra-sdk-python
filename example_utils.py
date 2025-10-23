# payra-sdk-python/example_utils.py

import os
from payra_sdk import PayraUtils

def run_example():
    # Convert USD/token to Wei
    amount_wei = PayraUtils.to_wei(3.34, 'polygon', 'usdt')
    print(amount_wei)  # 3340000

    # Convert Wei back to USD/token
    amount = PayraUtils.from_wei(3340000, 'polygon', 'usdt', precision=2)
    print(amount)  # "3.34"

    print("USDT decimals on Polygon:", PayraUtils.get_decimals("polygon", "usdt"))
    print("POL decimals on Polygon:", PayraUtils.get_decimals("polygon", "pol"))

    # Convert 100 EUR to USD
    # Only run currency conversion if API key is available
    if os.getenv("PAYRA_EXCHANGE_RATE_API_KEY"):
        usd_value = PayraUtils.convert_to_usd(100, "EUR")
        print(f"100 EUR = {usd_value} USD")
    else:
        print("Skipping currency conversion — PAYRA_EXCHANGE_RATE_API_KEY not set.")

if __name__ == "__main__":
    run_example()
