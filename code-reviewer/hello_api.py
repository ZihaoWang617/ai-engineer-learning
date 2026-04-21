import reviewer
import json
from datetime import datetime
from history import ReviewHistory
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
history = ReviewHistory()

class CodeInput(BaseModel):
    code: str = ""
    language: str = "python"
    model: str = "openai"
    filepath: str = ""

@app.get("/")
def read_root():
    return {"message": "Code Review API is running."}

@app.get("/greet/{name}")
def greet(name:str):
    return {"message": f"hello, {name}!"}

@app.post("/review")
def review_code(input: CodeInput):
    if input.filepath:
        try:
            with open(input.filepath, "r") as f:
                input.code = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail = "File not found.")
    if not input.code.strip():
        raise HTTPException(status_code = 400, detail = "Code content is empty.")
    

    if input.model.lower() == "openai":
        result = reviewer.review_with_openai(input.code)

    elif input.model.lower() == "anthropic":
        result = reviewer.review_with_anthropic(input.code)
    else:        
        raise HTTPException(status_code = 400, detail = "Invalid model. Use 'openai' or 'anthropic'.")
    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        raise HTTPException(status_code = 500, detail = "Failed to parse review result as JSON.")
    history.add_record(code=input.code, language=input.language, model=input.model, review=result)
    history.save_to_file("review_history.json")
    return result

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}  

@app.get("/history")
def get_history():
    return history.records