from datetime import datetime

from query import ask
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class QuestionInput(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Immigration Consulting API! Use the /ask endpoint to ask questions."}

@app.post("/ask")
def answer_question(input: QuestionInput):
    if not input.question.strip():
        raise HTTPException(status_code = 400, detail = "Question cannot be empty.")
    try:
        answer = ask(input.question)
        if not answer:
            raise HTTPException(status_code = 500, detail = "Failed to get an answer.")
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error processing the question: {str(e)}")    

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

