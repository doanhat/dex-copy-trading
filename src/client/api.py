import requests


class APIClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def __call__(self, http_method, endpoint):
        def decorator(func):
            def wrapper(*args, **kwargs):
                url = f"{self.base_url}/{endpoint.format(**kwargs)}"
                headers = self.headers.copy()
                params = kwargs.pop("params", {})
                if http_method == "GET":
                    response = requests.get(url, headers=headers, params=params)
                elif http_method == "POST":
                    data = kwargs.pop("data", {})
                    response = requests.post(
                        url, headers=headers, params=params, data=data
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {http_method}")
                response.raise_for_status()
                return func(response.json(), **kwargs)

            return wrapper

        return decorator
