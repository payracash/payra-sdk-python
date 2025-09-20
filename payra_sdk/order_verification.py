# payra-sdk-python/payra_sdk/order_verification.py

import os
import json
from dotenv import load_dotenv
from web3 import Web3
from payra_sdk.exceptions import InvalidArgumentError, SignatureError

# load env
load_dotenv()

class PayraOrderVerification:
    """
    SDK for verifying if an order has been paid using the Payra smart contract.
    """

    def __init__(self, network: str):
        self.network = network.upper()
        self.quicknode_url = self.get_quicknode_url(self.network)

        self.web3 = Web3(Web3.HTTPProvider(self.quicknode_url))
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to QuickNode RPC for {self.network}")

        self.merchant_id = os.getenv(f"PAYRA_{self.network}_MERCHANT_ID")
        self.forward_address = os.getenv(f"PAYRA_{self.network}_CORE_FORWARD_CONTRACT_ADDRESS")

        if not self.merchant_id:
            raise InvalidArgumentError(f"Missing PAYRA_{self.network}_MERCHANT_ID in .env")
        if not self.forward_address:
            raise InvalidArgumentError(f"Missing PAYRA_{self.network}_CORE_FORWARD_CONTRACT_ADDRESS in .env")

        # Load ABI
        abi_path = os.path.join(os.path.dirname(__file__), "contracts", "payraABI.json")
        with open(abi_path, "r") as f:
            self.abi = json.load(f)

        # find ABI parts
        self.core_fn = self.find_function(self.abi, "isOrderPaid")
        self.forward_fn = self.find_function(self.abi, "forward")

        # prepare forward contract
        self.forward_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.forward_address),
            abi=[self.forward_fn]
        )

    def is_order_paid(self, order_id: str) -> dict:
        """
        Calls the Payra Forward contract to check if an order is paid.
        """
        try:
            # encode isOrderPaid call manually
            core_fn_selector = self.function_selector(self.core_fn)
            encoded_params = self.web3.codec.encode(
                [inp["type"] for inp in self.core_fn["inputs"]],
                [int(self.merchant_id), order_id]
            )
            data = core_fn_selector + encoded_params.hex()

            # call forward()
            result = self.forward_contract.functions.forward("0x" + data).call()

            # decode result
            decoded = self.web3.codec.decode(
                [out["type"] for out in self.core_fn["outputs"]],
                result
            )
            return {
                "success": True,
                "paid": bool(decoded[0]),
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "paid": None,
                "error": str(e)
            }

    # === Helpers ===
    def get_quicknode_url(self, network: str) -> str:
        rpc_map = {
            "POLYGON": "https://warmhearted-ancient-shadow.matic.quiknode.pro/{API_KEY}",
            "ETHEREUM": "https://warmhearted-ancient-shadow.quiknode.pro/{API_KEY}",
            "LINEA": "https://warmhearted-ancient-shadow.linea-mainnet.quiknode.pro/{API_KEY}",
            "FLARE": "https://warmhearted-ancient-shadow.flare-mainnet.quiknode.pro/{API_KEY}/ext/bc/C/rpc/",
        }
        api_key = os.getenv("QUICK_NODE_RPC_API_KEY")
        if not api_key:
            raise InvalidArgumentError("QUICK_NODE_RPC_API_KEY is not set in .env")
        if network not in rpc_map:
            raise InvalidArgumentError(f"Unsupported network: {network}")
        return rpc_map[network].replace("{API_KEY}", api_key)

    def find_function(self, abi, name: str):
        for entry in abi:
            if entry.get("type") == "function" and entry.get("name") == name:
                return entry
        raise InvalidArgumentError(f"Function {name} not found in ABI!")

    def function_selector(self, fn: dict) -> str:
        """
        Generates the function selector (first 4 bytes of keccak of signature).
        """
        signature = f"{fn['name']}({','.join([inp['type'] for inp in fn['inputs']])})"
        return self.web3.keccak(text=signature)[:4].hex()
