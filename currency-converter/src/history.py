from .models import ConversionResult
import json
class ConversionHistory:
    """Manages currency conversion history with JSON file persistence.

    Attributes:
        filepath(str): The path to the JSON file where history records are stored.
        records(list[dict]): A list of conversion records loaded from the JSON file.
    """
    def __init__(self, filepath: str ='history.json'):
        """Initializes the conversion history manager.

        Args:
            filepath(str): The path to the JSON file where history records are stored.
        """
        self.filepath = filepath
        self.records = self.load()
    
    def load(self) -> list[dict]:
        """Loads the conversion history from the JSON file.

        Returns:
            A list of conversion records, where each record is a dictionary. 
            If the file does not exist, returns an empty list.
        """
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save(self):
        """Save the current conversion history to the JSON file.
        """
        with open(self.filepath, 'w') as f:
            json.dump(self.records, f, indent=4)

    def add_record(self, record: ConversionResult):
        """Adds a new conversion record to the history and saves it.

        Args:
            record(ConversionResult): The conversion result to add to the history.
        """
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
        """Filters the conversion history based on base and/or target currency.

        Args:
            base(str): The base currency to filter by.
            target(str): The target currency to filter by.

        Returns:
            A list of conversion records that match the filter criteria.
        """
        return [record for record in self.records if(not base or record['base'] == base) 
               and (not target or record['target'] == target)]
