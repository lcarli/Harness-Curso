# Desafio: detetive de documentação

Você já sabe falar com **um** provedor. Agora vai descobrir, sozinho, como falar com **qualquer** um.
Toda API de IA responde às mesmas **5 perguntas universais**. Sua missão: encontrá-las na documentação oficial.

## As 5 perguntas universais

| # | Pergunta | O que procurar na documentação |
|---|---|---|
| 1 | **Onde?** | O endereço (URL base) para onde mando o pedido. Existe um endereço compatível com o SDK da OpenAI? |
| 2 | **Quem?** | Como provo quem sou: onde gero a chave e em qual cabeçalho ela vai (ex.: `Authorization: Bearer`). |
| 3 | **Qual?** | O nome exato do modelo que vou usar. |
| 4 | **O que mando?** | O formato das mensagens (papéis `system`, `user`, `assistant`) e parâmetros (ex.: `temperature`). |
| 5 | **Onde está a resposta?** | Em que campo do JSON de volta vem o texto (e os tokens usados). |

## Sua investigação

Escolha 3 provedores (sugestões: **Mistral**, **Google Gemini**, **Groq** — ou outro de sua escolha).
Use apenas a **documentação oficial** de cada um. Anote o link de onde tirou cada informação.

| Pergunta | Provedor 1: ________ | Provedor 2: ________ | Provedor 3: ________ |
|---|---|---|---|
| 1. Onde? (URL base) | | | |
| 2. Quem? (chave / cabeçalho) | | | |
| 3. Qual? (um nome de modelo) | | | |
| 4. O que mando? (formato / parâmetros) | | | |
| 5. Onde está a resposta? (campo) | | | |
| Tem compatibilidade com o SDK da OpenAI? (sim / não / parcial) | | | |
| Link da documentação consultada | | | |

## Prova final (se tiver acesso)
Preencha um `.env` com o que você descobriu e rode `python aula2/02_chamada.py`
**sem mudar nenhuma linha de código**. Funcionou? Então você entendeu a ideia do curso.

## Sem acesso?
Peça ao Copilot Chat: *"Com base nesta tabela, monte o arquivo .env e explique o que eu veria ao rodar 02_chamada.py"*.
Depois confira, na documentação oficial, se o Copilot acertou — ele também pode errar!

## Perguntas para a discussão
- O que foi **igual** entre os 3 provedores? O que foi **diferente**?
- Alguma informação estava difícil de achar? Onde você a encontrou?
