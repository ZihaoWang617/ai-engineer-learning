import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [{"role": "system", "content": """You are a movie information assistant. 
             ##Response in JSON format with the follwoing keys: 
             # title: 
             # year:
             # director: 
             # genre: list of strings
             # summary:"""}]
question = input("What movie you want to know about?")
if question.lower() == 'q':
    print("Exiting the program.")
    exit()
messages.append({"role":"user","content":question})
response = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages,
    temperature = 0,
    response_format = {"type": "json_object"},
)
ai_reply = response.choices[0].message.content
data = json.loads(ai_reply)
print(f"Title: {data['title']}")
print(f"Year: {data['year']}")
print(f"Director: {data['director']}")
print(f"Genre: {', '.join(data['genre'])}")
print(f"Summary: {data['summary']}")