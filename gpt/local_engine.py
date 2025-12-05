import requests


def local_llm(question):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": question}
    )
    return res.json().get("response")
