from datetime import datetime
from agent_basic import agent
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import re

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
        raise HTTPException(status_code = 400, detail = "Question cannot be empty.")
    
    try:
        result = agent.invoke(
        {"messages": [HumanMessage(content = input.question)]},
        config = {"configurable": {"thread_id": input.session_id}}
        )

        if not result:
            raise HTTPException(status_code = 500, detail = "Failed to get an answer.")
        messages = result["messages"]
        human_idx = None
        for i in range(len(messages) -1, -1, -1):
            if messages[i].type == "human":
                human_idx = i
                break
        if human_idx is None:
            raise HTTPException(status_code = 500, detail = "No human message found in agent result")
        
        new_messages = messages[human_idx:]

        answer = new_messages[-1].content

        sources = []
        for msg in new_messages:
            if msg.type == "tool":
                matches = re.findall(r"\[来源：(.+?)\]", msg.content)
                sources.extend(matches)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error processing the question: {str(e)}")    

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

