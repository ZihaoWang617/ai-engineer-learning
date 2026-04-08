import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [{"role": "system", "content": "You are a helpful assistant."}]
while True:
    question = input("Enter your question (type q to quit):")
    if question.lower() == 'q':
        print("exiting the program.")
        break
    try:
        messages.append({"role":"user","content":question})
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature= 0.2,
            stream = True,
        )
        memory = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                memory += content 
                print(content, end = "", flush = True)
        print()
        messages.append({"role": "assistant", "content": memory})
    except Exception as e:
        print(f"Error: {e}")
        break