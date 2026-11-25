"""Demo - How much did this call cost? tokens x price."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

# Fill with your provider's current price per 1M tokens (in US$).
# Check the provider's pricing page: prices change often. Free/local = 0.
PRECO_ENTRADA_POR_MILHAO = 0.40  # example value only
PRECO_SAIDA_POR_MILHAO = 1.60   # example value only
COTACAO_DOLAR = 5.50  # US$ -> R$ (fill with today's rate)

r = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {"role": "system", "content": "Você é a Aurora, do Café Aurora. Responda em português."},
        {"role": "user", "content": "Sugira um combo de café da manhã com 2 itens."},
    ],
)
print("Aurora:", r.choices[0].message.content)

if not r.usage:
    print("\nEste provedor não informou o uso de tokens.")
else:
    entrada, saida = r.usage.prompt_tokens, r.usage.completion_tokens
    custo_usd = (entrada * PRECO_ENTRADA_POR_MILHAO + saida * PRECO_SAIDA_POR_MILHAO) / 1_000_000
    print(f"\nTokens: {entrada} de entrada + {saida} de saída")
    print(f"Custo desta chamada: US$ {custo_usd:.6f} (≈ R$ {custo_usd * COTACAO_DOLAR:.6f})")
    # Scale it up: what if Aurora answers 1,000 customers a day for 30 days?
    print(f"1.000 conversas/dia por 30 dias: ≈ R$ {custo_usd * COTACAO_DOLAR * 30_000:.2f}")
