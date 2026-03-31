from .models import ConversionResult
import json
def save_record(record: ConversionResult):
    history = load_history()
    record_dict = {
        "base": record.request.base,
        "target": record.request.target,
        "amount": record.request.amount,
        "result": record.converted_amount,
        "rate": record.rate
    }
    history.append(record_dict)
    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)

def load_history() -> list[dict]:
    try:
        with open("history.json", "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []