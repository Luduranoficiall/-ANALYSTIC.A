import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def cloud_llm(question):
    r = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role":"user","content":question}]
    )
    return r.choices[0].message["content"]
