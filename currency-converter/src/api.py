from  typing import Optional
import requests

def fetch_exchange_rate(base: str, target: str) -> Optional[float]:
    api_url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(api_url)
    data = response.json()
    if data['result'] == 'success':
        rates = data['rates']
        return rates.get(target)
    else:
        return None

