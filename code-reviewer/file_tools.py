def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file '{filepath}' not found."
    except UnicodeDecodeError:
        return f"Error: file '{filepath}' is not valid UTF-8 text."
    except OSError as e:
        return f"Error reading '{filepath}': {e}"


openai_tools = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a local file and return its content",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "the code file to be reviewed"
                }
            },
            "required": ["filepath"]

        }
    }
}]

anthropic_tools = [{
    "name": "read_file",
    "description": "Read a local file and return its content",
    "input_schema": {
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "the code file to be reviewed"
            }
        },
        "required": ["filepath"]
    }
}]

available_functions = {
    "read_file": read_file,
}
