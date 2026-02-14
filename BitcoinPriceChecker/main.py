import requests
import json

def get_bitcoin_price():
    """
    Retrieves the current price of Bitcoin from the Coingecko API.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        price = data['bitcoin']['usd']
        print(f"The current price of Bitcoin is: {price}")

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except (KeyError, TypeError) as e:
        print(f"Error parsing API response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    get_bitcoin_price()