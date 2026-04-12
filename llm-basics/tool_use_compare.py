from dotenv import load_dotenv
import requests
import os
import json
from anthropic import Anthropic
from openai import OpenAI

def get_exchange_rate(base: str, target: str) -> str:
    url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(url)
    data = response.json()
    if data["result"] == "success":
        rates = data["rates"][target]
        return f"1 {base} = {rates} {target}"
    else:
        return "failed to get currency."

openai_tools = [{
    "type": "function",
    "function":{
        "name": "get_exchange_rate",
        "description": "Get the current exchange rate between two currencies",
        "parameters": {
            "type": "object",
            "properties":{
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
}]
anthropic_tools = [{
    "name": "get_exchange_rate",
    "description": "Get the current exchange rate between two currencies",
    "input_schema": {
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
}]

load_dotenv()
Anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
OpenAI_api_key = os.getenv("OPENAI_API_KEY")

client1 = OpenAI(api_key = OpenAI_api_key)
client2 = Anthropic(api_key = Anthropic_api_key)

question = input("what's your question? ")

def ask_openai(question):
    messages = [{"role": "system", "content": "You are a helpful assistant that provides exchange rates between currencies. If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters."}]
    messages.append({"role": "user", "content": question})
    response = client1.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        temperature = 0,
        tools = openai_tools,
    )
    if response.choices[0].message.tool_calls is not None:
        tool_call = response.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        messages.append(response.choices[0].message)
        messages.append({"role": "tool","tool_call_id": tool_call.id, "content": get_exchange_rate(**arguments)})
        final_response = client1.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature = 0,
        )
        print(final_response.choices[0].message.content)
    else: 
        print(response.choices[0].message.content)



def ask_anthropic(question):
    messages = []
    messages.append({"role": "user", "content": question})
    response = client2.messages.create(
        model = "claude-sonnet-4-20250514",
        system = "You are a helpful assistant that provides exchange rates between currencies. If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters.",
        max_tokens = 1024,
        messages = messages,
        tools = anthropic_tools,
    )
    tool_used = False
    for block in response.content:
        if block.type == "tool_use":
            tool_used = True
            arguments = block.input
            result = get_exchange_rate(**arguments)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role":"user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                }]
            })
    if tool_used:
        final_response = client2.messages.create(
        model = "claude-sonnet-4-20250514",
        system = "You are a helpful assistant that provides exchange rates between currencies. If the user asks for an exchange rate, call the get_exchange_rate function with the appropriate parameters.",
        max_tokens = 1024,
        messages = messages,
    )
        print(f"AI_reply:", final_response.content[0].text)
    else:
        print(response.content[0].text)



print("=== OpenAI ===")
ask_openai(question)

print("\n=== Anthropic ===")
ask_anthropic(question)



