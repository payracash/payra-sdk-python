# payra-sdk-python/example_order_is_paid.py

from payra_sdk import PayraOrderService, PayraSDKException

ORDER_ID = "ord-258"

def run_example():
    try:
        order_service = PayraOrderService("polygon") #select network
        result = order_service.is_paid(ORDER_ID)

        print("\nChecking order status...")
        print("Order ID:", ORDER_ID)
        print("Result:", result)

        if result["success"] and result["paid"]:
            print("Order is PAID")
        elif result["success"]:
            print("Order is NOT paid yet")
        else:
            print("Error:", result["error"])

    except PayraSDKException as e:
        print(f"SDK error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_example()
