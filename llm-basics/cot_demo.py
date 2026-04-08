import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
messages = [{"role": "system", "content": "You are a helpful assistant."}]
question = "I have 3 boxes. Each box contains 2 bags. Each bag contains 4 marbles. I remove 5 marbles total. How many marbles remain?"
response = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages + [{"role": "user", "content": question}],
    temperature= 0
)
print(response.choices[0].message.content)

messages = [{"role": "system", "content": "You are a helpful assistant. Think step by step before giving your final answer."}]
question = "I have 3 boxes. Each box contains 2 bags. Each bag contains 4 marbles. I remove 5 marbles total. How many marbles remain?"
response = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages + [{"role": "user", "content": question}],
    temperature= 0
)
print(response.choices[0].message.content)