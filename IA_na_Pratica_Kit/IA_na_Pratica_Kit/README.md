# Kit de demos — IA na Prática (6 aulas)

Projeto fio condutor: **Aurora**, a assistente virtual do **Café Aurora** (fictício).
O curso ensina a consumir **qualquer** API de IA. Todos os scripts usam o mesmo
cliente genérico (biblioteca `openai`, compatível com vários provedores) e leem
a configuração de um arquivo `.env` com apenas 3 linhas: `BASE_URL`, `API_KEY`, `MODEL`.

## Estrutura

```
.env.example                     modelo de configuração (copie para .env)
requirements.txt                 bibliotecas (openai, python-dotenv)
.github/workflows/testes-aurora.yml   Aula 6: testes automáticos a cada pull request

aula1/  Harness — sem código
  .github/copilot-instructions.md     instruções sempre ligadas da Aurora
  .github/prompts/cardapio.prompt.md  comando /cardapio
  gabarito.md                         "Seu primeiro teste"

aula2/  Fale com qualquer IA
  01_chamada.http                chamada crua (extensão REST Client)
  02_chamada.py                  a mesma chamada em Python (+ tokens e finish_reason)
  03_chat_com_memoria.py         chat com histórico
  04_resposta_json.py            resposta em JSON validada
  05_custo.py                    calcula o custo de uma chamada
  painel.py                      Painel da Aurora: chat + abas Pedido, Resposta, Memória e Tokens
  erros.md                       erros universais e o que fazer
  detetive.md                    desafio "detetive de documentação"

aula3/  Agentes
  .github/agents/aurora-gerente.agent.md   agente personalizado em Markdown
  dados/estoque.csv, dados/vendas.csv      dados fictícios
  agente_aurora.py                         agente em Python (modelo + ferramentas + loop)

aula4/  RAG
  docs/manual_aurora.md          manual fictício do café
  rag_aurora.py                  mini-RAG sem embeddings (funciona com qualquer provedor)
  rag_como_ferramenta.py         o agente da Aula 3 com a ferramenta buscar_no_manual

aula5/  Testes I
  golden.csv                     conjunto golden (~30 casos)
  sistema_aurora.md              instruções da Aurora usadas nos testes (edite aqui, sem mexer no código)
  avaliador.py                   roda os casos, aplica critérios, gera relatorio.csv
  respostas_simuladas.csv        respostas prontas para o modo --simular (sem API)

aula6/  Testes II
  checagens.py                   checagens automáticas (privacidade, segurança, formato)
  mudancas.md                    registro de mudanças (governança)
  triagem.md                     guia de triagem de falhas
```

> O workflow do GitHub Actions fica em `.github/workflows/` **na raiz** do repositório,
> porque é só lá que o GitHub procura workflows.

## Preparação (uma vez, ~30 min)

1. Instale o **Python 3.10+**, o **VS Code**, a extensão **Python** e a extensão **REST Client**.
2. No terminal do VS Code, dentro da pasta do kit:
   ```
   python -m venv .venv
   # Windows:      .venv\Scripts\activate
   # macOS/Linux:  source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e deixe descomentado **um** bloco (o do seu provedor).
4. Para a chamada `.http` da Aula 2, copie também o `.env` para dentro de `aula2/`
   (o REST Client procura o `.env` na mesma pasta do arquivo `.http`).
5. Teste: `python aula2/02_chamada.py`. Se aparecer uma resposta da Aurora, está pronto.

Comandos das aulas (sempre a partir da pasta raiz do kit):
```
python aula2/02_chamada.py
python aula2/painel.py              # abre o Painel da Aurora no navegador (ou: --simular)
python aula3/agente_aurora.py
python aula4/rag_aurora.py "O croissant tem glúten?"
python aula5/avaliador.py            # ou: python aula5/avaliador.py --simular
python aula6/checagens.py
```

Plano B: abra o repositório num **GitHub Codespace** (já vem com Python e VS Code no navegador).

## Opções de provedor

| Opção | O que precisa | BASE_URL | Observação |
|---|---|---|---|
| GitHub Models | Conta GitHub + token com `models:read` | `https://models.github.ai/inference` | Gratuito com limites de uso. Modelo ex.: `openai/gpt-4.1-mini` |
| OpenAI | Chave paga | `https://api.openai.com/v1` | |
| Claude (compatibilidade) | Chave paga da Anthropic | `https://api.anthropic.com/v1/` | Confira na documentação as limitações atuais da compatibilidade |
| Ollama (local) | Ollama instalado + modelo baixado | `http://localhost:11434/v1` | Sem custo; `API_KEY` pode ser qualquer texto |
| Sem acesso | Só VS Code + Copilot | — | Cole o código no Copilot Chat e peça: "explique e simule a saída deste script". Na Aula 5 use `python aula5/avaliador.py --simular` |

> Nomes de modelos, preços e limites mudam com frequência. **Consulte a documentação do seu provedor** antes da aula.

### Recursos que variam entre provedores
- **Ferramentas (tool calling)** — usadas nas Aulas 3 e 4. Nem todo modelo/provedor suporta. Confira na documentação.
- **Resposta em JSON (`response_format`)** — o script da Aula 2 tem plano B automático.
- **Embeddings** — nem todo provedor oferece; por isso o RAG da Aula 4 usa busca por palavras-chave.

## Segurança das chaves
- A chave fica **só** no `.env`. Nunca no código, em slides, prints ou mensagens.
- O `.gitignore` já ignora `.env` (em qualquer pasta), `.venv` e `__pycache__`.
- Vazou? **Revogue** a chave no site do provedor e crie outra. Apagar o arquivo não basta.
- Prefira chaves com permissão mínima e limite de gasto configurado.
- No GitHub Actions use **secrets** (nunca escreva a chave no workflow).
