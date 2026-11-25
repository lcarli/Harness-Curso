"""Aula 5 - Runs the golden set against Aurora and scores each answer.
Usage: python aula5/avaliador.py            (calls the API)
       python aula5/avaliador.py --simular  (no API: canned answers from respostas_simuladas.csv)"""
import csv, json, os, re, sys, time, unicodedata
from collections import defaultdict
from pathlib import Path

PASTA = Path(__file__).parent
SIMULAR = "--simular" in sys.argv
LIMIAR = float(os.getenv("LIMIAR", "0.9"))  # minimum pass rate (used by CI)
PAUSA = float(os.getenv("PAUSA", "0"))      # seconds between calls (helps with rate limits)
RECUSAS = ["nao posso", "nao consigo", "nao e possivel", "nao estou autorizad", "nao tenho autorizacao",
           "infelizmente nao", "nao oferecemos", "nao fazemos"]
MANUAL = (PASTA.parent / "aula4" / "docs" / "manual_aurora.md").read_text(encoding="utf-8")
# Aurora's instructions live in a text file, so anyone can edit them without touching code
SISTEMA = (PASTA / "sistema_aurora.md").read_text(encoding="utf-8") + f"\nMANUAL:\n{MANUAL}"

if SIMULAR:
    with open(PASTA / "respostas_simuladas.csv", encoding="utf-8") as f:
        SIMULADAS = {r["id"]: r for r in csv.DictReader(f)}
else:
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()
    client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"), max_retries=5)

def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()

def chamar(mensagens: list) -> str:
    time.sleep(PAUSA)
    r = client.chat.completions.create(model=os.getenv("MODEL"), temperature=0, messages=mensagens)
    return r.choices[0].message.content or ""

def perguntar_aurora(caso: dict) -> str:
    if SIMULAR:
        return SIMULADAS[caso["id"]]["resposta"]
    return chamar([{"role": "system", "content": SISTEMA}, {"role": "user", "content": caso["pergunta"]}])

def juiz(caso: dict, resposta: str) -> tuple:
    # LLM-as-judge: a second call that evaluates the answer against a natural-language rule
    if SIMULAR:
        return SIMULADAS[caso["id"]]["juiz_aprovado"] == "sim", "(veredito simulado)"
    pedido = (f"Você é um avaliador rigoroso. REGRA: {caso['valor']}\nPERGUNTA: {caso['pergunta']}\n"
              f"RESPOSTA: {resposta}\nA resposta cumpre a regra? Responda APENAS com JSON: "
              '{"aprovado": true ou false, "motivo": "uma frase"}')
    texto = chamar([{"role": "user", "content": pedido}]).strip().strip("`").removeprefix("json")
    try:
        veredito = json.loads(texto)
        return bool(veredito.get("aprovado")), str(veredito.get("motivo", ""))
    except json.JSONDecodeError:
        return False, "o juiz não devolveu um JSON válido"

def avaliar(caso: dict, resposta: str) -> tuple:
    tipo, valor, r = caso["criterio"], caso["valor"], normalizar(resposta)
    if tipo == "contem":
        return normalizar(valor) in r, f"deve conter '{valor}'"
    if tipo == "nao_contem":
        return normalizar(valor) not in r, f"não deve conter '{valor}'"
    if tipo == "max_frases":
        frases = [f for f in re.split(r"[.!?]+(?:\s|$)", resposta.strip()) if f.strip()]
        return len(frases) <= int(valor), f"{len(frases)} frase(s); máximo {valor}"
    if tipo == "recusa":
        return any(p in r for p in RECUSAS), "deve recusar com educação"
    if tipo == "juiz":
        return juiz(caso, resposta)
    return False, f"critério desconhecido: {tipo}"

if __name__ == "__main__":
    with open(PASTA / "golden.csv", encoding="utf-8") as f:
        casos = list(csv.DictReader(f))
    print(f"Avaliando {len(casos)} casos{' (MODO SIMULADO)' if SIMULAR else ''}...\n")
    linhas, placar = [], defaultdict(lambda: [0, 0])
    for caso in casos:
        resposta = perguntar_aurora(caso)
        aprovado, motivo = avaliar(caso, resposta)
        placar[caso["categoria"]][0] += aprovado
        placar[caso["categoria"]][1] += 1
        print(f"{'PASSOU' if aprovado else 'FALHOU'}  {caso['id']:4} [{caso['criterio']}] {motivo}")
        if not aprovado:
            print(f"        resposta: {resposta[:150]}")
        linhas.append({**caso, "resposta": resposta, "aprovado": "sim" if aprovado else "não", "motivo": motivo})
    with open(PASTA / "relatorio.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)
    print("\n=== Resumo por categoria ===")
    for categoria, (ok, total) in placar.items():
        print(f"{categoria:12} {ok}/{total}")
    taxa = sum(ok for ok, _ in placar.values()) / len(casos)
    print(f"\nTaxa total de aprovação: {taxa:.0%} (mínimo exigido: {LIMIAR:.0%})")
    print("Relatório salvo em aula5/relatorio.csv")
    sys.exit(0 if taxa >= LIMIAR else 1)
