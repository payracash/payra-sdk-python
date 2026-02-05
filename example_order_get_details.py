# payra-sdk-python/example_order_get_details.py

from payra_sdk import PayraOrderService, PayraSDKException

ORDER_ID = "ord-258"

def run_example():
    try:
        order_service = PayraOrderService("polygon") #select network
        details = order_service.get_details(ORDER_ID)

        print("\nGet order details...")
        print("Order ID:", ORDER_ID)
        print("Details:", details)

    except PayraSDKException as e:
        print(f"SDK error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_example()
