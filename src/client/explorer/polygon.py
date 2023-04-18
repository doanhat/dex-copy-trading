from src.client.api import APIClient

client = APIClient(
    base_url="https://api.polygonscan.com/",
    headers={
        "accept": "application/json"
    })


@client('GET', '/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}')
def get_contract_abi(response, **kwarg):
    return response
