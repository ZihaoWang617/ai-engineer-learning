from datetime import datetime
from rag_basics.langchain_query_pinecone import ask
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class QuestionInput(BaseModel):
    question: str
    session_id: str = "default"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Immigration Consulting API! Use the /ask endpoint to ask questions."}

@app.post("/ask")
def answer_question(input: QuestionInput):
    if not input.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        result = ask(input.question, session_id=input.session_id)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "links": result["links"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the question: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}