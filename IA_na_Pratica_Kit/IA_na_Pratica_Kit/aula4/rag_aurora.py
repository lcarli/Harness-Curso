"""Demo 2 - Mini-RAG without embeddings: search, join, answer (works with any provider)."""
import os, re, sys, unicodedata
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

MANUAL = Path(__file__).parent / "docs" / "manual_aurora.md"
STOPWORDS = set("a o as os de da do das dos e é em no na nos nas um uma para por com sem que "
                "qual quais quando como onde se ou ao à vocês voce voces tem ter meu minha "
                "eu me isso esse essa este esta mais muito pode posso".split())

# ---------- PHASE 1: PREPARE (split the manual into small pieces) ----------
def normalizar(texto: str) -> str:
    # lowercase and remove accents: "Glúten" -> "gluten"
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()

def carregar_trechos(tamanho: int = 500, sobra: int = 80) -> list:
    texto = MANUAL.read_text(encoding="utf-8")
    trechos = []
    for bloco in re.split(r"\n(?=## )", texto):  # one block per "## " heading
        linhas = bloco.strip().splitlines()
        secao, corpo = linhas[0].lstrip("# ").strip(), "\n".join(linhas[1:])
        atual = ""
        for paragrafo in [p.strip() for p in corpo.split("\n\n") if p.strip()]:
            if atual and len(atual) + len(paragrafo) > tamanho:
                trechos.append({"secao": secao, "texto": atual})
                atual = "..." + atual[-sobra:]  # small overlap keeps context between pieces
            atual = (atual + "\n" + paragrafo).strip()
        if atual:
            trechos.append({"secao": secao, "texto": atual})
    return trechos

# ---------- PHASE 2: SEARCH (simple keyword scoring) ----------
def termos(texto: str) -> set:
    # crude stemming: keep the first 5 letters, so "encomenda" and "encomendas" match
    palavras = re.findall(r"[a-z0-9]+", normalizar(texto))
    return {p[:5] for p in palavras if p not in STOPWORDS and len(p) > 2}

def buscar_trechos(pergunta: str, k: int = 3) -> list:
    procurados = termos(pergunta)
    pontuados = [(len(procurados & termos(t["secao"] + " " + t["texto"])), t) for t in carregar_trechos()]
    pontuados = [p for p in pontuados if p[0] > 0]
    return sorted(pontuados, key=lambda p: p[0], reverse=True)[:k]

# ---------- PHASE 3: ANSWER (prompt with the retrieved pieces) ----------
def montar_prompt(pergunta: str, achados: list) -> str:
    contexto = "\n\n".join(f"[Seção: {t['secao']}]\n{t['texto']}" for _, t in achados)
    return ("Responda SOMENTE com base nos trechos abaixo; cite a seção usada. "
            "Se a resposta não estiver nos trechos, diga 'Não encontrei isso no manual'.\n\n"
            f"TRECHOS:\n{contexto or '(nenhum trecho encontrado)'}\n\nPERGUNTA: {pergunta}")

def responder(pergunta: str) -> str:
    load_dotenv()
    client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
    r = client.chat.completions.create(model=os.getenv("MODEL"), temperature=0, messages=[
        {"role": "system", "content": "Você é a Aurora, do Café Aurora. Responda em português, em até 3 frases."},
        {"role": "user", "content": montar_prompt(pergunta, buscar_trechos(pergunta))}])
    return r.choices[0].message.content

# ---------- OPTIONAL: search by meaning (embeddings) ----------
# Some providers offer an embeddings endpoint (client.embeddings.create); others don't.
# Check your provider's docs for availability and the embedding model name.
# def buscar_por_embeddings(pergunta, trechos, modelo_embeddings="NOME_DO_MODELO"):
#     client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
#     textos = [pergunta] + [t["texto"] for t in trechos]
#     vetores = [d.embedding for d in client.embeddings.create(model=modelo_embeddings, input=textos).data]
#     similar = lambda a, b: sum(x * y for x, y in zip(a, b))  # dot product = closeness of meaning
#     notas = [similar(vetores[0], v) for v in vetores[1:]]
#     return sorted(zip(notas, trechos), key=lambda p: p[0], reverse=True)[:3]

if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or input("Pergunta para o manual: ")
    achados = buscar_trechos(pergunta)
    print("\n=== Trechos recuperados ===")
    for nota, t in achados:
        print(f"\n[pontos: {nota}] Seção: {t['secao']}\n{t['texto']}")
    if not achados:
        print("(nenhum trecho com palavras em comum)")
    print("\n=== Resposta da Aurora ===")
    print(responder(pergunta))
