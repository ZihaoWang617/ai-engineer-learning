import requests

base_url = "http://127.0.0.1:8000"

def health_check():
    response = requests.get(f"{base_url}/health")
    return response.json()

def review_code(code, language="python", model="openai"):
    response = requests.post(f"{base_url}/review", json = {
        "code": code,
        "language": language,
        "model": model
    })
    return response.json()

if __name__ == "__main__":
    print("===Health Check===")
    print(health_check())

    print("\n===Code Review Test===")
    code = """
def add(a, b):
    return "a"
"""
    result = review_code(code)
    print("Summary:", result["summary"])
    print("Rating:", result["rating"])