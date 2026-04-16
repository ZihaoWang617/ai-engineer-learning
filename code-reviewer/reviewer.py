import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
import prompts
import file_tools

load_dotenv()
SYSTEM_MESSAGE = prompts.SYSTEM_PROMPT + "\n\n" + prompts.COT_INSTRUCTION + "\n\n" + prompts.FEW_SHOT_EXAMPLE
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def build_user_prompt(content: str, is_filepath: bool) -> str:
    if is_filepath:
        return (
            "Review the Python code in this file.\n"
            f"File path: {content}\n"
            "Use the read_file tool to fetch the file contents before reviewing."
        )
    return f"Review this Python code:\n```python\n{content}\n```"


def review_with_openai(content: str, is_filepath: bool = False) -> str:
    client = get_openai_client()
    messages = [{
        "role": "system",
        "content": SYSTEM_MESSAGE
    }]
    messages.append({"role": "user", "content": build_user_prompt(content, is_filepath)})
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0,
            tools=file_tools.openai_tools,
        )

        message = response.choices[0].message
        while message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                function_to_call = file_tools.available_functions[tool_call.function.name]
                arguments = json.loads(tool_call.function.arguments)
                result = function_to_call(**arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0,
                tools=file_tools.openai_tools,
            )
            message = response.choices[0].message

        messages.append(message)

        memory = message.content or ""
        if memory:
            print(memory, end="", flush=True)
        print()
        return memory
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"
    
def review_with_anthropic(content: str, is_filepath: bool = False) -> str:
    client = get_anthropic_client()
    messages = [{
        "role": "user",
        "content": build_user_prompt(content, is_filepath),
    }]
    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            system=SYSTEM_MESSAGE,
            max_tokens=1024,
            messages=messages,
            tools=file_tools.anthropic_tools,
        )

        while any(block.type == "tool_use" for block in response.content):
            messages.append({"role": "assistant", "content": response.content})
            for block in response.content:
                if block.type != "tool_use":
                    continue
                function_to_call = file_tools.available_functions[block.name]
                result = function_to_call(**block.input)
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }],
                })

            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                system=SYSTEM_MESSAGE,
                max_tokens=1024,
                messages=messages,
                tools=file_tools.anthropic_tools,
            )

        memory = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        if memory:
            print(memory, end="", flush=True)
        print()
        return memory
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"



