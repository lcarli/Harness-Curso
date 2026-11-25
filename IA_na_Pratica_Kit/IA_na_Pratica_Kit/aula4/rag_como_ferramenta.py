"""Demo - RAG as a tool: the Aula 3 agent gains a new tool, buscar_no_manual."""
import importlib.util
from pathlib import Path

PASTA = Path(__file__).parent

def importar(caminho: Path):
    # load a .py file as a module (lets us reuse code from other lesson folders)
    spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

rag = importar(PASTA / "rag_aurora.py")
agente = importar(PASTA.parent / "aula3" / "agente_aurora.py")

# ---------- the new tool: reuses the retrieval from rag_aurora.py ----------
def buscar_no_manual(pergunta: str) -> str:
    achados = rag.buscar_trechos(pergunta)
    if not achados:
        return "Nenhum trecho encontrado no manual."
    return "\n\n".join(f"[Seção: {t['secao']}]\n{t['texto']}" for _, t in achados)

agente.FERRAMENTAS["buscar_no_manual"] = buscar_no_manual
agente.ETIQUETAS.append(agente.etiqueta(
    "buscar_no_manual",
    "Busca trechos do manual do Café Aurora (horários, preços, alergênicos, trocas, "
    "encomendas, Wi-Fi, fidelidade). Use para qualquer pergunta sobre regras do café.",
    {"pergunta": {"type": "string", "description": "a dúvida, em poucas palavras"}},
    ["pergunta"]))

SISTEMA = agente.SISTEMA + (" Para dúvidas sobre regras, preços ou alergênicos, use buscar_no_manual "
                            "e cite a seção. Se não encontrar, diga 'Não encontrei isso no manual'.")

if __name__ == "__main__":
    historico = [{"role": "system", "content": SISTEMA}]
    print("Aurora com manual. Ex.: 'Quero 60 pães de queijo para sábado. Tem estoque e qual a regra?'")
    while (texto := input("\nVocê: ")).strip().lower() != "sair":
        agente.rodar_agente(texto, historico)
