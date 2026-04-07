import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [
    {"role": "system", "content": """You are a python code reviewer.
     ##Task
     Review the user's code and identify issues.
     
     ##Output Format
     Line [number]: [issue description]
     Fixed code: [fixed code]
     
     ##Example
     user's code: def add(a,b): return a+b
     output:
     Line 1: Missing hints.
     Fixed code: def add(a: int, b: int) -> int:
     """}     
]

def get_multiline_input() -> str:
    print("enter your code(type 'END' on a new line to stop)")
    lines = []
    while True:
        line = input()
        if line.lower() == 'q':
            return 'q'
        elif line.lower() == "end":
            break
        lines.append(line)
    return "\n".join(lines)


while True:
    question = get_multiline_input()
    if question.lower() == 'q':
        print("Exiting the program.")
        break
    try:
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature = 0,
        )
        ai_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_reply})
        print(ai_reply)
        print(f"\n[Tokens usage: input = {response.usage.prompt_tokens}, output = {response.usage.completion_tokens}, total = {response.usage.total_tokens}]")
    except Exception as e:
        print(f"Error: {e}")
        break

