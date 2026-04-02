from dataclasses import dataclass

@dataclass
class ConversionRequest:
    """Represents a currency conversion request.

    Attributes:
        amount(float): The amount to convert.
        base(str): the base currency code (e.g., 'USD').
        target(str): the target currency code (e.g., 'EUR').
    """
    amount: float
    base: str
    target: str

@dataclass
class ConversionResult:
    """Represents the result of a currency conversion.

    Attributes:
        request(ConversionRequest): The original conversion request.
        rate(float): The exchange rate used for the conversion.
        converted_amount(float): The amount after conversion.
    """
    request: ConversionRequest
    rate: float
    converted_amount: float

