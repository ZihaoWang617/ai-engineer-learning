import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
import prompts

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
def review_with_openai(code: str)-> str:
    messages = [{
        "role": "system",
        "content": prompts.SYSTEM_PROMPT + "\n\n" + prompts.COT_INSTRUCTION + "\n\n" + prompts.FEW_SHOT_EXAMPLE
    }]
    messages.append({"role":"user","content":code})
    try:
        response = openai_client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature = 0,
            stream = True,
        )
        memory = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                memory += content
                print(content, end = "", flush = True)
        print()
        return memory
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
    
def review_with_anthropic(code: str) -> str:
    messages = []
    messages.append({"role": "user", "content": code})
    memory = ""
    with anthropic_client.messages.stream(
        model = "claude-sonnet-4-20250514",
        system = prompts.SYSTEM_PROMPT + "\n\n" + prompts.COT_INSTRUCTION + "\n\n" + prompts.FEW_SHOT_EXAMPLE,
        max_tokens = 1024,
        messages = messages,
    ) as stream:
        for text in stream.text_stream:
            print(text,end = "", flush = True)
            memory += text
    print()
    return memory



