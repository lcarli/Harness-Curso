"""Demo - Chat WITH memory: the program keeps and resends the whole history."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
AURORA = "Você é a Aurora, assistente do Café Aurora. Responda em português, de forma curta."

historico = [{"role": "system", "content": AURORA}]  # the conversation memory

print("Converse com a Aurora (digite 'sair' para terminar).")
while True:
    texto = input("\nVocê: ")
    if texto.strip().lower() == "sair":
        break
    historico.append({"role": "user", "content": texto})
    r = client.chat.completions.create(model=os.getenv("MODEL"), messages=historico)
    resposta = r.choices[0].message.content
    historico.append({"role": "assistant", "content": resposta})  # this line gives memory
    print("Aurora:", resposta)
    print(f"   (mensagens enviadas nesta chamada: {len(historico) - 1})")

# Experiment: comment out the "historico.append(... assistant ...)" line,
# run again and ask "qual foi minha primeira pergunta?". What changes?
