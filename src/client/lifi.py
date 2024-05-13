from src.client.api import APIClient

client = APIClient(
    base_url="https://li.quest/v1", headers={"accept": "application/json"}
)


@client("GET", "quote")
def get_quote(response):
    return response


@client("GET", "status")
def get_status(response):
    return response


@client("POST", "quote/contractCall")
def post_contract_call(response, **kwargs):
    return response
