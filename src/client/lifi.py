from src.client.api import APIClient

client = APIClient(
    base_url="https://li.quest/v1",
    headers={
        "accept": "application/json"
    })


@client('GET', 'quote')
def get_quote(response):
    return response


@client('POST', 'quote')
def get_quote(response):
    return response
