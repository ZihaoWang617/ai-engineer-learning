from dataclasses import dataclass

@dataclass
class ConversionRequest:
    amount: float
    base: str
    target: str

@dataclass
class ConversionResult:
    request: ConversionRequest
    rate: float
    converted_amount: float

