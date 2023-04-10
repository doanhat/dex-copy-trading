import requests


class APIClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def __call__(self, method, endpoint):
        def decorator(func):
            def wrapper(*args, **kwargs):
                url = f"{self.base_url}/{endpoint.format(**kwargs)}"
                headers = self.headers.copy()
                params = kwargs.pop('params', {})
                response = requests.request(method, url, headers=headers, params=params)
                response.raise_for_status()
                return func(response.json(), **kwargs)
            return wrapper
        return decorator
