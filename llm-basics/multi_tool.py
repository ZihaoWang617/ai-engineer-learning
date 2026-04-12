import os
import requests
import json
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

def get_weather(city: str) -> str:
    api_url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(api_url)
    return f"{city}: {response.text.strip()}"

def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

tools = [
    {
        "type": "function",
        "function":{
            "name": "get_exchange_rate",
            "description": "get the current exchange rate between base curency and target currency",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "the base currency code, e.g. USD"
                    },
                    "target": {
                        "type": "string",
                        "description": "the target currency code, e.g. EUR"
                    }
                },
                "required": ["base", "target"]
            }
        }
    },
    {
        "type":"function",
        "function": {
            "name": "get_weather",
            "description": "get the current weather conditions and temperature for a specific city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "the specific city we want to get the weather"
                    }
                },
            "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "receive a string math expression, calculate the expression in string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": { 
                        "type": "string",
                        "description": "the mathematic expression in string type."
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
available_functions = {
    "get_exchange_rate": get_exchange_rate,
    "get_weather": get_weather,
    "calculate": calculate,
}
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [{
    "role": "system", "content": """
    ##You are a helpful assistant that provide exchange currency, get current weather base on specific city and can calculate math. 
    ##If the user ask for these, call the function and decide base on specific question.
      """
}]
question = input("What's your question?")
messages.append({"role":"user", "content": question})
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages = messages,
    tools = tools,
    temperature = 0,
)

print(f"[DEBUG] tool_calls: {response.choices[0].message.tool_calls}")
print(f"[DEBUG] content: {response.choices[0].message.content}")

if response.choices[0].message.tool_calls is not None:
    tool_call = response.choices[0].message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    function_to_call = available_functions[tool_call.function.name]
    result = function_to_call(**arguments)
    messages.append(response.choices[0].message)
    messages.append({"role": "tool", "tool_call_id": tool_call.id,"content": result})
    final_response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        temperature = 0,
    )
    print(final_response.choices[0].message.content)
else:
    print(response.choices[0].message.content)
