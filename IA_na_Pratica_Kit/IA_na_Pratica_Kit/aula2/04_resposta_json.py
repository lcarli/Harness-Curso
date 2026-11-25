"""Demo - Asking for a JSON answer and validating it (the test of this lesson)."""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
MODEL = os.getenv("MODEL")

PEDIDO = [
    {"role": "system", "content": (
        "Você é a Aurora, do Café Aurora. Horários: seg a sáb 7h às 19h; dom 8h às 13h. "
        'Responda APENAS com um JSON no formato {"horario": "...", "dia": "..."} e nada mais.')},
    {"role": "user", "content": "Que horas vocês abrem no domingo?"},
]

try:
    # Plan A: ask the provider to force JSON output
    r = client.chat.completions.create(model=MODEL, messages=PEDIDO,
                                       response_format={"type": "json_object"})
    print("(usando response_format = json_object)")
except Exception as erro:
    # Plan B: some providers/models do not support response_format; rely on the prompt only
    print(f"(response_format não suportado: {type(erro).__name__}; pedindo só no prompt)")
    r = client.chat.completions.create(model=MODEL, messages=PEDIDO)

texto = r.choices[0].message.content.strip()
print("Resposta bruta:", texto)

# Some models wrap JSON in ```json ... ``` fences; remove them before parsing
if texto.startswith("```"):
    texto = texto.strip("`").removeprefix("json").strip()

try:
    dados = json.loads(texto)
    tem_campos = "horario" in dados and "dia" in dados
    print("Horário:", dados.get("horario"), "| Dia:", dados.get("dia"))
    print("Teste do JSON:", "OK" if tem_campos else "FALHOU (faltam campos)")
except json.JSONDecodeError:
    print("Teste do JSON: FALHOU (não é um JSON válido)")
