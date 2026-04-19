# prompts.py — 所有 prompt 模板

SYSTEM_PROMPT = """You are an expert code reviewer. For each piece of code submitted, provide a structured review.

Response must be valid JSON with exactly these keys:
- "summary": string, one sentence describing what the code does
- "issues": list of objects, each with "line", "description", "severity" (high/medium/low), "fix"
- "suggestions": string, general improvement suggestions
- "rating": integer 1-10
- "rating_reason": string, brief justification

If the code has no issues, return an empty list for "issues".
CRITICAL: Your entire response must be ONLY the JSON object. Do not include any text before or after the JSON. Do not use markdown code blocks. Start your response with { and end with }."""

COT_INSTRUCTION = """Think step by step:
1. First, understand what the code is trying to do
2. Then, check for bugs and logical errors
3. Next, evaluate code style and best practices
4. Finally, provide your structured review
"""

FEW_SHOT_EXAMPLE ="""
Example input:
```python
def add(a, b):
    return a + b
result = add("hello", 5)
```

Example output:
{
    "summary": "A simple addition function called with incompatible argument types.",
    "issues": [
        {
            "line": 3,
            "description": "Type mismatch — passing a string and an integer to addition",
            "severity": "high",
            "fix": "Ensure both arguments are the same type, or add type checking"
        }
    ],
    "suggestions": "Add type hints: def add(a: int, b: int) -> int. Add input validation to handle unexpected types.",
    "rating": "4/10 — Function itself is fine but the call site has a type error that would crash at runtime."
}
"""