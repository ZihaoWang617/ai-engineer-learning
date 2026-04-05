import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
messages = [
    {"role": "system", "content": "You are a translator assistant. You will translate user's Chinese text to English. Respond in JSON format with keys: original, translation, notes. Just output the JSON object without any additional text."},]
while True:
    question = input("What is your question? ")
    if question.lower() =='q':
        print("Exiting the program.")
        break
    try:
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        ai_reply = response.choices[0].message.content
        try:
            data = json.loads(ai_reply)
            print(f"原文：{data['original']}")
            print(f"翻译：{data['translation']}")
            print(f"备注：{data['notes']}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
        messages.append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        print(f"Error: {e}")
        break 


