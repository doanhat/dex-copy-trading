from src.client.api import APIClient
from src.conf.config import config, ETH_ADDRESS

client = APIClient(
    base_url="https://pro-openapi.debank.com/v1",
    headers={
        "accept": "application/json",
        "AccessKey": config['DEBANK_ACCESS_KEY']
    })


@client('GET', 'user/token')
def get_user_token_balance(response):
    return response
