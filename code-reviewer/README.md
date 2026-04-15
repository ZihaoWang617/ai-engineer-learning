# Code Reviewer

A CLI tool that reviews your Python code using OpenAI (GPT-4o-mini) or Anthropic (Claude Sonnet) with streaming output.

## Features

- **Dual Model Support**: Choose between OpenAI GPT-4o-mini and Anthropic Claude Sonnet for code review
- **Streaming Output**: Real-time response display as the model generates its review
- **File Reading**: Provide a file path to automatically read and review the code
- **Direct Input**: Paste code directly into the terminal for review
- **Structured Review**: Every review includes Summary, Issues Found, Suggestions, and Rating

## Tech Stack

- Python 3.9
- OpenAI API (GPT-4o-mini)
- Anthropic API (Claude Sonnet)

## Project Structure

- `prompts.py` — System prompt, Chain-of-Thought instruction, and few-shot example
- `file_tools.py` — File reading function and tool definitions for both APIs
- `reviewer.py` — Core review logic with streaming for both OpenAI and Anthropic
- `main.py` — Entry point with user interaction loop

## Setup

1. Install dependencies:
```bash
   pip install openai anthropic python-dotenv
```

2. Create a `.env` file in the `code-reviewer/` directory: