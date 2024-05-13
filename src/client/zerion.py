from src.client.api import APIClient
from src.conf.config import config, ETH_ADDRESS

client = APIClient(
    base_url="https://api.zerion.io/v1",
    headers={
        "accept": "application/json",
        "authorization": f"Basic {config['ZERION_AUTH_KEY']}",
    },
)


@client("GET", "chains")
def get_chains(response):
    return response["data"]


@client("GET", "wallets/{address}/portfolio")
def get_wallet_portfolio(response, **kwargs):
    return response["data"]


@client("GET", "wallets/{address}/transactions")
def get_wallet_transactions(response, **kwargs):
    return response["data"]


@client("GET", "swap/offers")
def get_swap_offer(response, **kwargs):
    return response["data"]


def get_token_address(token_info: dict, chain):
    filters = [lambda x: x["chain_id"] == chain]
    results = list(
        filter(lambda x: all([f(x) for f in filters]), token_info["implementations"])
    )
    address = results[0]["address"]
    return address if address and address != "" else ETH_ADDRESS
