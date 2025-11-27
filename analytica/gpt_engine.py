# ============================================
# file: gpt_engine.py
# ============================================
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_insights(question):
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Você é o ANALYTIC.A PRO, um analista de BI muito avançado, humano e extremamente profissional."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message["content"]
