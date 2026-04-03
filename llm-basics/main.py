import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},]
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
        print(f'AI: {response.choices[0].message.content}\n')
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
    except Exception as e:
        print(f"Error: {e}")
        break 


