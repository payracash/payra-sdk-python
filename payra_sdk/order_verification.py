# payra-sdk-python/payra_sdk/order_verification.py

import os
import json
import random
from dotenv import load_dotenv
from web3 import Web3
from .utils import PayraUtils
from .exceptions import InvalidArgumentError, SignatureError

# load env
load_dotenv()

class PayraOrderVerification:
    """
    SDK for verifying if an order has been paid using the Payra smart contract.
    """

    def __init__(self, network: str):
        self.network = network.upper()
        self.rpc_url = self.get_rpc_url(self.network)

        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to QuickNode RPC for {self.network}")

        self.merchant_id = os.getenv(f"PAYRA_{self.network}_MERCHANT_ID")
        self.gateway_address = os.getenv(f"PAYRA_{self.network}_OCP_GATEWAY_CONTRACT_ADDRESS")

        if not self.merchant_id:
            raise InvalidArgumentError(f"Missing PAYRA_{self.network}_MERCHANT_ID in .env")
        if not self.gateway_address:
            raise InvalidArgumentError(f"Missing PAYRA_{self.network}_OCP_GATEWAY_CONTRACT_ADDRESS in .env")

        # Load ABI
        abi_path = os.path.join(os.path.dirname(__file__), "contracts", "payraABI.json")
        with open(abi_path, "r") as f:
            self.abi = json.load(f)

        self.user_data_contract = self.get_user_data_contract()

    def get_user_data_contract(self):
        """
        Internal helper to initialize Payra contracts.
        It fetches the UserData contract address from the Gateway registry.
        """
        # Initialize Gateway Contract
        gateway_contract = self.web3.eth.contract(address=self.gateway_address, abi=self.abi)
        
        # getRegistryDetails
        _, _, user_data_address, _ = gateway_contract.functions.getRegistryDetails().call()
        
        # Return the actual contract responsible for order data
        return self.web3.eth.contract(address=user_data_address, abi=self.abi)

    def is_order_paid(self, order_id: str) -> dict:
        """
        Verify if an order is paid on Payra contract.
        """
        try:
            # Using the resolved user_data_contract
            is_paid = self.user_data_contract.functions.isOrderPaid(
                int(self.merchant_id), 
                order_id
            ).call()

            return {
                "success": True,
                "paid": bool(is_paid),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "paid": None,
                "error": str(e)
            }

    def get_order_status(self, order_id: str) -> dict:
        """
        Detailed status of an order from Payra smart contract.
        Equivalent to getOrderDetails in Node.js version.
        """
        try:
            # Calls getOrderDetails
            order = self.user_data_contract.functions.getOrderDetails(
                int(self.merchant_id), 
                order_id
            ).call()

            # Mapping the returned tuple/struct to a dictionary
            # Order struct: [paid, token, amount, fee, timestamp]
            return {
                "success": True,
                "error": None,
                "paid": bool(order[0]),
                "token": order[1],
                "amount": int(order[2]),
                "fee": int(order[3]),
                "timestamp": int(order[4]),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "paid": None,
                "token": None,
                "amount": None,
                "fee": None,
                "timestamp": None,
            }
            
    def get_rpc_url(self, network: str) -> str:
        """
        Collects all PAYRA_{NETWORK}_RPC_URL_i variables and randomly picks one.
        """

        urls = []
        i = 1
        while True:
            env_key = f"PAYRA_{network}_RPC_URL_{i}"
            value = os.getenv(env_key)
            if not value:
                break
            urls.append(value.strip())
            i += 1

        if not urls:
            raise InvalidArgumentError(f"No RPC URLs found for network: {network}")

        return random.choice(urls)