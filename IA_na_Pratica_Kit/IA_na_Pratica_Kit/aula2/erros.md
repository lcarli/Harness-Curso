# Erros universais (valem para qualquer provedor)

Toda API de IA conversa por HTTP. Por isso os **códigos de erro são os mesmos** em todo lugar.
Leia a mensagem completa: ela quase sempre diz o que está errado.

| Código | O que significa | Causa mais comum | O que fazer |
|---|---|---|---|
| **401** Unauthorized | "Não sei quem você é" | Chave errada, vazia, expirada ou com espaço/aspas sobrando | Confira a linha `API_KEY` no `.env` (sem aspas, sem espaços). Gere uma chave nova se preciso. |
| **403** Forbidden | "Sei quem você é, mas você não pode" | Chave sem permissão (ex.: token do GitHub sem `models:read`), conta sem crédito, modelo não liberado para você | Revise as permissões da chave e o plano/créditos da conta. |
| **404** Not Found | "Não achei o que você pediu" | `BASE_URL` errada (faltou `/v1`, sobrou uma barra) ou nome do `MODEL` errado | Compare `BASE_URL` e `MODEL` com a documentação do provedor, letra por letra. |
| **400** Bad Request | "Seu pedido está malformado" | JSON inválido, parâmetro não suportado por aquele provedor/modelo | Remova parâmetros extras (ex.: `response_format`, `tools`) e teste de novo. |
| **429** Too Many Requests | "Calma! Muitos pedidos" | Limite de uso por minuto/dia atingido (comum em planos gratuitos) | Espere alguns segundos/minutos e tente de novo. Em turma, não rodem todos ao mesmo tempo. |
| **5xx** (500, 502, 503) | "O problema é do lado de lá" | Provedor instável ou sobrecarregado | Não é culpa sua. Espere e tente de novo; veja a página de status do provedor. |

## Outros problemas comuns
- **`Connection refused` / `Connection error`**: o endereço não responde. No Ollama, verifique se ele está aberto.
- **`ModuleNotFoundError: No module named 'openai'`**: ative a `.venv` e rode `pip install -r requirements.txt`.
- **`api_key` vazia / `None`**: o `.env` não foi encontrado. Ele deve se chamar exatamente `.env` (não `.env.txt`).

## Chave segura: 5 regras
1. A chave mora **só** no `.env`.
2. O `.env` **nunca** vai para o Git (o `.gitignore` cuida disso).
3. Nada de chave em print, slide, e-mail ou chat.
4. Vazou? **Revogue** no site do provedor e crie outra.
5. Configure **limite de gasto** quando o provedor permitir.
