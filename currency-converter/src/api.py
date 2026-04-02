from  typing import Optional
import requests

def fetch_exchange_rate(base: str, target: str) -> Optional[float]:
    """Fetch the exchange rate between two currencies from the API.

    Args:
        base(str): The base currency code(e.g., 'USD').
        target(str): The target currency code(e.g., 'EUR').
    
    Returns:
        The exchange rate as a float, or None if the request fails.
    """
    api_url = f"https://open.er-api.com/v6/latest/{base}"
    try:
        response = requests.get(api_url)
        data = response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None
    if data['result'] == 'success':
        rates = data['rates']
        return rates.get(target)
    else:
        return None

