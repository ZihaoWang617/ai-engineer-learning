import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key = api_key)
messages = []
while True:
    question = input("What is your question? ")
    if question.lower() == 'q':
        print("Exiting.")
        break
    try:
        messages.append({"role": "user", "content": question})
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            system = "You are a helpful assistant. Answer the user's question concisely.",
            messages=messages,
            max_tokens=1024,
)
        ai_reply = response.content[0].text
        print(f"AI: {ai_reply}")
        messages.append({"role": "assistant", "content": ai_reply})
    except Exception as e:
        print(f"Error: {e}")
        break 