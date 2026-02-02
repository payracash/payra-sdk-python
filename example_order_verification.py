# payra-sdk-python/example_order_verification.py

from payra_sdk import PayraOrderVerification, PayraSDKException

ORDER_ID = "ord-258"

def run_example():
    try:
        verifier = PayraOrderVerification("polygon") #select network
        result = verifier.is_order_paid(ORDER_ID)

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
