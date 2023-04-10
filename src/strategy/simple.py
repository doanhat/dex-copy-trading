import json
import pathlib
from typing import List, Dict

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from src.client.lifi import get_quote
from src.client.zerion import get_wallet_transactions
from src.conf.config import config

chains_map = json.loads((pathlib.Path(__file__).parent.parent / "resources" / "chains_map.json")
                        .read_text(encoding="UTF-8"))


def place_order(token_map, chain):
    # Connect wallet
    web3 = Web3(HTTPProvider(chains_map[chain]['rpc']))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    wallet = web3.eth.account.from_key(config['PRIVATE_KEY'])

    # Get quote with Li.Fi
    quote = get_quote(
        params={
            "fromChain": chains_map[chain]['id'],
            "toChain": chains_map[chain]['id'],
            "fromToken": token_map['out']['symbol'],
            "toToken": token_map['in']['symbol'],
            "fromAddress": wallet.address,
            "fromAmount": 1000000,
            "order": "RECOMMENDED"
        }
    )

    # Approve
    contract_address = quote['transactionRequest']['to']
    contract_abi = web3.eth.contract(contract_address).abi
    # Send transaction
    transaction = quote['transactionRequest']
    transaction['gas'] = web3.to_int(hexstr=quote['transactionRequest']['gasLimit'])
    transaction['value'] = web3.to_int(hexstr=transaction['value'])
    transaction['nonce'] = web3.eth.get_transaction_count(wallet.address)

    del transaction['gasLimit']
    signed_trx = web3.eth.account.sign_transaction(transaction, config['PRIVATE_KEY'])
    trx_hash = web3.to_hex(web3.eth.send_raw_transaction(signed_trx['rawTransaction']))

    print("")


def update_last_transactions_list(adr, last_transactions_dict, transaction_hash):
    last_transactions_dict[adr] = transaction_hash
    (pathlib.Path(__file__).parent.parent / "resources" / "last_transactions.json").write_text(
        data=json.dumps(last_transactions_dict), encoding="UTF-8")


def copy_transactions(address: List, last_transactions: Dict):
    for adr in address:
        saved_last_transaction = last_transactions.get(adr, None)
        onchain_last_transaction = get_wallet_transactions(
            address=adr,
            params={
                'currency': 'usd',
                'page[size]': 1,
                'filter[operation_types]': 'trade',
                'filter[asset_types]': 'fungible'
            }
        )
        if onchain_last_transaction[0]['attributes']['hash'] != saved_last_transaction:
            chain = onchain_last_transaction[0]['relationships']['chain']['data']['id']
            token_map = {
                token['direction']: token['fungible_info'] for token in
                onchain_last_transaction[0]['attributes']['transfers']
            }
            place_order(token_map, chain)
            # update_last_transactions_list(adr, last_transactions, onchain_last_transaction[0]['attributes']['hash'])
            print("")
