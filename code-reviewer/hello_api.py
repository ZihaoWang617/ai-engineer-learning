from fastapi import FastAPI
import reviewer

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello world"}

@app.get("/greet/{name}")
def greet(name:str):
    return {"message": f"hello, {name}!"}

from pydantic import BaseModel
class CodeInput(BaseModel):
   code: str
   language: str = "python"

@app.post("/review")
def review_code(input: CodeInput):
    result = reviewer.review_with_openai(input.code)
    return {"review": result}