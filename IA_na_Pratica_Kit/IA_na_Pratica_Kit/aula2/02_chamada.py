"""Demo 2 - The same raw call, now in Python (works with any OpenAI-compatible provider)."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads BASE_URL, API_KEY and MODEL from the .env file
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

SISTEMA = ("Você é a Aurora, assistente do Café Aurora. Responda em português, em até 3 frases. "
           "Fatos: seg a sáb 7h às 19h; dom 8h às 13h; pão de queijo sai às 7h e às 16h.")

resposta = client.chat.completions.create(
    model=os.getenv("MODEL"),
    temperature=0.3,  # lower = more predictable answers
    messages=[
        {"role": "system", "content": SISTEMA},
        {"role": "user", "content": "Que horas sai o pão de queijo?"},
    ],
)

# The useful parts of the response
escolha = resposta.choices[0]
print("Aurora:", escolha.message.content)
print("\n--- bastidores ---")
print("Modelo que respondeu:", resposta.model)
print("Motivo de parada (finish_reason):", escolha.finish_reason)
if resposta.usage:  # some providers may not return usage
    print("Tokens de entrada:", resposta.usage.prompt_tokens)
    print("Tokens de saída:  ", resposta.usage.completion_tokens)
    print("Total de tokens:  ", resposta.usage.total_tokens)
