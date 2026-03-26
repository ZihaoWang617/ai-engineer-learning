from typing import Optional
from .api import fetch_exchange_rate
from .models import ConversionRequest, ConversionResult

def convert_currency(request: ConversionRequest) -> Optional[ConversionResult]:
    rate = fetch_exchange_rate(base=request.base, target=request.target)
    if rate is not None:
        converted_amount = request.amount * rate
        return ConversionResult(request=request, rate=rate, converted_amount=converted_amount)
    else:
        return None