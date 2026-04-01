from .models import ConversionResult
import json
class ConversionHistory:
    def __init__(self, filepath: str ='history.json'):
        self.filepath = filepath
        self.records = self.load()
    
    def load(self) -> list[dict]:
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.records, f, indent=4)

    def add_record(self, record: ConversionResult):
        record_dict = {
            "base": record.request.base,
            "target": record.request.target,
            "amount": record.request.amount,
            "result": record.converted_amount,
            "rate": record.rate
        }
        self.records.append(record_dict)
        self.save()

    def filter(self, base: str = '', target: str = '') -> list[dict]:
        return [record for record in self.records if(not base or record['base'] == base) 
               and (not target or record['target'] == target)]
