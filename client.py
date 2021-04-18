from binance.client import Client


def authent(func):
    def wrapper(*args, **kwargs):
        kwargs["client"] = client()
        return func(*args, **kwargs)
    return wrapper


def client():
    with open("API_KEY.txt", "r") as f:
        api_key = f.read()
    
    with open("API_SECRET.txt", "r") as f:
        api_secret = f.read()

    return Client(api_key, api_secret)
