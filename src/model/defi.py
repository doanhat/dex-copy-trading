import json
import pathlib

from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from src.client.lifi import get_quote
from src.client.zerion import get_wallet_transactions, get_token_address
from src.conf.config import config, ERC20_ABI, ETH_ADDRESS


class Strategy:
    SIMPLE = "simple"
    CHAINS_MAP = json.loads(
        (
            pathlib.Path(__file__).parent.parent / "resources" / "chains_map.json"
        ).read_text(encoding="UTF-8")
    )

    def __init__(self):
        self.AMOUNT = 1000000000000
        self.GAS_LIMIT = 5000000
        self.RATIO = 1

    def execute(self, mode, **kwargs):
        if mode == self.SIMPLE:
            smart_money_wallets = kwargs["smart_money_wallets"]
            last_transactions_dict = kwargs["last_transactions_dict"]

            def update_last_transactions_list(
                adr, last_transactions: dict, transaction_hash
            ):
                last_transactions[adr] = transaction_hash
                (
                    pathlib.Path(__file__).parent.parent
                    / "resources"
                    / "last_transactions.json"
                ).write_text(data=json.dumps(last_transactions), encoding="UTF-8")

            def copy_transactions():
                for adr in smart_money_wallets:
                    saved_last_transaction = last_transactions_dict.get(adr, None)
                    onchain_last_transaction = get_wallet_transactions(
                        address=adr,
                        params={
                            "currency": "usd",
                            "page[size]": 1,
                            "filter[operation_types]": "trade",
                            "filter[asset_types]": "fungible",
                        },
                    )
                    if (
                        onchain_last_transaction[0]["attributes"]["hash"]
                        != saved_last_transaction
                    ):
                        chain = onchain_last_transaction[0]["relationships"]["chain"][
                            "data"
                        ]["id"]
                        token_map = {
                            token["direction"]: {
                                **token["fungible_info"],
                                **token["quantity"],
                            }
                            for token in onchain_last_transaction[0]["attributes"][
                                "transfers"
                            ]
                        }
                        self.make_transaction(token_map, chain)
                        update_last_transactions_list(
                            adr,
                            last_transactions_dict,
                            onchain_last_transaction[0]["attributes"]["hash"],
                        )
                        print("DONE !")

            copy_transactions()

    def check_and_set_allowance(
        self,
        web3,
        wallet: LocalAccount,
        token_address,
        approval_address,
        amount,
        gas,
        chain,
    ):
        # Transactions with the native token don't need approval
        if token_address != ETH_ADDRESS:  # ETH

            erc20 = web3.eth.contract(
                address=web3.to_checksum_address(token_address), abi=ERC20_ABI
            )

            allowance = erc20.functions.allowance(
                wallet.address, approval_address
            ).call()

            if allowance < amount:
                txn = {
                    "chainId": self.CHAINS_MAP[chain]["id"],
                    "from": web3.to_checksum_address(wallet.address),
                    "to": web3.to_checksum_address(token_address),
                    "gas": int(gas),
                    "gasPrice": web3.eth.gas_price,
                    "nonce": web3.eth.get_transaction_count(wallet.address),
                    "data": erc20.encodeABI(
                        fn_name="approve", args=[approval_address, amount]
                    ),
                }

                # Sign and send the transaction
                signed_txn = wallet.sign_transaction(txn)
                txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                web3.eth.wait_for_transaction_receipt(txn_hash)

    def make_transaction(self, token_map, chain):
        # Connect wallet
        web3 = Web3(HTTPProvider(self.CHAINS_MAP[chain]["rpc"], {"timeout": 60}))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        wallet = web3.eth.account.from_key(config["PRIVATE_KEY"])
        # Get quote with Li.Fi
        quote = get_quote(
            params={
                "fromChain": self.CHAINS_MAP[chain]["id"],
                "toChain": self.CHAINS_MAP[chain]["id"],
                "fromToken": get_token_address(token_map["out"], chain),
                "toToken": get_token_address(token_map["in"], chain),
                "fromAddress": wallet.address,
                "fromAmount": int(token_map["out"]["int"]) // self.RATIO,
                "order": "RECOMMENDED",
            }
        )

        # Check token balance in wallet
        # token_balance = get_user_token_balance(
        #     params={
        #         "chain_id": self.CHAINS_MAP[chain]['debankId'],
        #         "id": wallet.address,
        #         "token_id": get_token_address(token_map['out'], chain)
        #     }
        # )

        if (
            web3.to_int(hexstr=quote["transactionRequest"]["gasLimit"])
            <= self.GAS_LIMIT
            and int(quote["estimate"]["gasCosts"][0]["estimate"]) <= self.GAS_LIMIT
        ):
            self.check_and_set_allowance(
                web3,
                wallet,
                quote["action"]["fromToken"]["address"],
                quote["estimate"]["approvalAddress"],
                self.AMOUNT,
                quote["estimate"]["gasCosts"][0]["estimate"],
                chain,
            )

            # Send transaction
            transaction = quote["transactionRequest"]
            transaction["gas"] = web3.to_int(
                hexstr=quote["transactionRequest"]["gasLimit"]
            )
            transaction["value"] = web3.to_int(hexstr=transaction["value"])
            transaction["nonce"] = web3.eth.get_transaction_count(wallet.address)

            del transaction["gasLimit"]
            signed_trx = web3.eth.account.sign_transaction(
                transaction, config["PRIVATE_KEY"]
            )
            trx_hash = web3.to_hex(
                web3.eth.send_raw_transaction(signed_trx["rawTransaction"])
            )

            return trx_hash
