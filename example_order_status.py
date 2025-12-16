# payra-sdk-python/example_order_verification.py

from payra_sdk import PayraOrderVerification, PayraSDKException

ORDER_ID = "ORDER-1765138911744-126-5"

def run_example():
    try:
        verifier = PayraOrderVerification("polygon") #select network
        result = verifier.get_order_status(ORDER_ID)

        print("\nGet order status...")
        print("Order ID:", ORDER_ID)
        print("Result:", result)

    except PayraSDKException as e:
        print(f"SDK error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_example()
