import uuid
from datetime import datetime
from pydantic import BaseModel, Field
import json

class ReviewRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    code: str
    language: str = "python"
    model: str = "openai"
    review: dict

class ReviewHistory:
    def __init__(self):
        self.records: list[ReviewRecord] = self.load()

    def load(self) -> list[ReviewRecord]:
        try:
            with open("review_history.json", "r") as f:
                data = json.load(f)
                return [ReviewRecord(**record) for record in data]
        except FileNotFoundError:
            return []
    
    def save_to_file(self, filename:str):
        with open(filename, "w") as f:
            json.dump([record.dict() for record in self.records], f, indent=4)

    def add_record(self, code: str, language: str = "python", model: str = "openai", review: dict = None):
        record = ReviewRecord(code=code, language=language, model=model, review=review)
        self.records.append(record) # type: ignore

