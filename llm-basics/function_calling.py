import requests
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

def get_exchange_rate(base: str, target: str) -> str:
    api_url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(api_url)
    data = response.json()
    if data["result"] == "success":
        rates = data["rates"][target]
        return f"1 {base} = {rates}{target}"
    else:
        return "Failed to get exchange rate."

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get the current exchange rate between two currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "The base currency code, e.g. USD"
                    },
                    "target": {
                        "type": "string",
                        "description": "The target currency code, e.g. CNY"
                    }
                },
                "required": ["base", "target"]
            }
        } 
    }  
]
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [
    {"role": "system", "content": "You are a helpful assistant that provides exchange rates between currencies. If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters."}
]

question = input( "What's your question? (Type 'q' to quit): ")
messages.append({"role": "user", "content": question})
response = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages,
    tools = tools,
    temperature = 0,
)

print(f"[DEBUG] tool_calls: {response.choices[0].message.tool_calls}")
print(f"[DEBUG] content: {response.choices[0].message.content}")

if response.choices[0].message.tool_calls is not None:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    messages.append(response.choices[0].message)
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": get_exchange_rate(**arguments)})
    final_response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        temperature = 0,
)
    print(final_response.choices[0].message.content)
else:
    print(response.choices[0].message.content)



