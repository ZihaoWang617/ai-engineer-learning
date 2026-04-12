import os
import anthropic
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

def get_exchange_rate(base: str, target: str) -> str:
    api_url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(api_url)
    data = response.json()
    if data["result"] =="success":
        rates = data["rates"][target]
        return f"1{base} ={rates}{target}"
    else:
        return "failed to get the exchange rate."
    
tools = [{
        "name": "get_exchange_rate",
        "description": "get the exchange rate between two currencies",
        "input_schema": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "the base currency code. e.g. USD"},
                "target": {"type": "string", "description": "the target currency code. e.g. CNY"}
            },
            "required": ["base","target"]
        }
    }]   

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key = api_key)
messages =[]
question = input("What's your question?")
messages.append({"role":"user", "content": question})
response = client.messages.create(
    model = "claude-sonnet-4-20250514",
    system = "You are a helpful assistant that provides exchange rates between base and target currencies.If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters.",
    messages = messages,
    max_tokens = 1024,
    tools = tools,
)
for block in response.content:
    if block.type == "tool_use":
        arguments = block.input
        result = get_exchange_rate(**arguments)
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user", 
            "content": [{
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            }]
        })
final_response = client.messages.create(
        model = "claude-sonnet-4-20250514",
        system = "You are a helpful assistant that provides exchange rates between base and target currencies.If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters.",
        messages = messages,
        max_tokens = 1024,
    )
print(f"AI_reply:", final_response.content[0].text)
