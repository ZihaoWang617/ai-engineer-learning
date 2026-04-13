def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file '{filepath}' not found."


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