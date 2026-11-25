"""Demo 3 - A real agent: model + tools + loop (any provider with tool calling)."""
import csv, json, os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
MODEL = os.getenv("MODEL")
DADOS = Path(__file__).parent / "dados"
MAX_PASSOS = 6  # safety brake: avoids infinite loops (and runaway cost)

# ---------- 1) THE TOOLS (real functions, run by OUR program, not by the model) ----------
def consultar_estoque(produto: str) -> str:
    with open(DADOS / "estoque.csv", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["produto"].lower() == produto.lower():
                return f"{linha['quantidade']} {linha['unidade']}"
    return "produto não encontrado"

def calcular_falta(necessario: int, disponivel: int) -> str:
    falta = max(0, int(necessario) - int(disponivel))
    return f"faltam {falta}" if falta else "não falta nada"

def registrar_encomenda(produto: str, quantidade: int) -> str:
    # Write action: a human must confirm (human-in-the-loop)
    ok = input(f"\n   >>> Confirmar encomenda de {quantidade} x {produto}? (s/n) ")
    if ok.strip().lower() != "s":
        return "encomenda CANCELADA pelo usuário"
    with open(DADOS / "encomendas.txt", "a", encoding="utf-8") as f:
        f.write(f"{produto};{quantidade}\n")
    return "encomenda registrada"

FERRAMENTAS = {"consultar_estoque": consultar_estoque, "calcular_falta": calcular_falta,
               "registrar_encomenda": registrar_encomenda}

# ---------- 2) THE LABELS (the only thing the model sees about each tool) ----------
def etiqueta(nome, descricao, propriedades, obrigatorios):
    return {"type": "function", "function": {"name": nome, "description": descricao,
            "parameters": {"type": "object", "properties": propriedades, "required": obrigatorios}}}

ETIQUETAS = [
    etiqueta("consultar_estoque", "Retorna a quantidade em estoque de um produto do café.",
             {"produto": {"type": "string", "description": "ex.: pão de queijo, café"}}, ["produto"]),
    etiqueta("calcular_falta", "Calcula quantas unidades faltam para atender uma necessidade.",
             {"necessario": {"type": "integer"}, "disponivel": {"type": "integer"}},
             ["necessario", "disponivel"]),
    etiqueta("registrar_encomenda", "Registra uma encomenda ao fornecedor. Só use se o usuário pedir.",
             {"produto": {"type": "string"}, "quantidade": {"type": "integer"}}, ["produto", "quantidade"]),
]

SISTEMA = ("Você é a Aurora, gerente virtual do Café Aurora. Use as ferramentas para consultar dados "
           "reais antes de responder. Considere 1 pão de queijo e 1 café por pessoa. "
           "Nunca registre encomendas sem o usuário pedir. Responda em português, de forma curta.")

# ---------- 3) THE LOOP (think -> act -> observe -> repeat) ----------
def rodar_agente(pergunta: str, historico: list) -> None:
    historico.append({"role": "user", "content": pergunta})
    for passo in range(1, MAX_PASSOS + 1):
        r = client.chat.completions.create(model=MODEL, messages=historico, tools=ETIQUETAS)
        msg = r.choices[0].message
        if not msg.tool_calls:  # no tool requested: this is the final answer
            historico.append({"role": "assistant", "content": msg.content or ""})
            print(f"\nAurora: {msg.content}")
            return
        historico.append(msg.model_dump(exclude_none=True))  # keep the model's tool request
        for chamada in msg.tool_calls:  # the model only ASKS; our program executes
            nome = chamada.function.name
            args = json.loads(chamada.function.arguments or "{}")
            funcao = FERRAMENTAS.get(nome)
            resultado = funcao(**args) if funcao else f"ferramenta desconhecida: {nome}"
            print(f"[passo {passo}] {nome}({', '.join(repr(v) for v in args.values())}) -> {resultado}")
            historico.append({"role": "tool", "tool_call_id": chamada.id, "content": resultado})
    print("\n(limite de passos atingido: o agente parou por segurança)")

if __name__ == "__main__":
    historico = [{"role": "system", "content": SISTEMA}]
    print("Agente Aurora. Exemplo: 'Dá para atender 30 pessoas amanhã?'  (digite 'sair')")
    while (texto := input("\nVocê: ")).strip().lower() != "sair":
        rodar_agente(texto, historico)

# ---------- CHALLENGE TEMPLATE (uncomment, move ABOVE the "if __name__" line, adapt) ----------
# def ver_cardapio_do_dia() -> str:
#     return "espresso, cappuccino, pão de queijo, croissant, bolo de cenoura"
# FERRAMENTAS["ver_cardapio_do_dia"] = ver_cardapio_do_dia
# ETIQUETAS.append(etiqueta("ver_cardapio_do_dia", "Lista os itens do cardápio de hoje.", {}, []))
