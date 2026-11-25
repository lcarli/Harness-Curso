# Registro de mudanças da Aurora

Toda mudança na Aurora — por menor que seja — entra aqui **antes** de ir para produção.
Regra de ouro: **nenhuma mudança sem teste rodado e sem aprovação de outra pessoa.**

## O que conta como mudança
| Tipo | Exemplos |
|---|---|
| **Prompt** | Trocar uma palavra nas instruções, mudar o tom, adicionar uma regra |
| **Dados** | Atualizar o manual, preços, estoque, cardápio |
| **Fluxo** | Nova ferramenta no agente, mudar o número máximo de passos, mudar a busca do RAG |
| **Modelo** | Trocar o modelo ou o provedor (`MODEL`, `BASE_URL`) |

## Modelo de registro (copie para cada mudança)

| Campo | Preencha |
|---|---|
| Data | |
| Quem fez | |
| Tipo (prompt / dados / fluxo / modelo) | |
| O que mudou (antes → depois) | |
| Motivo (por que mudar?) | |
| Link do pull request | |
| Resultado dos testes antes (taxa total) | |
| Resultado dos testes depois (taxa total) | |
| Casos que mudaram de resultado | |
| Novos casos adicionados ao golden | |
| Aprovado por | |
| Decisão (publicar / ajustar / desfazer) | |

## Exemplo preenchido

| Campo | Preencha |
|---|---|
| Data | 10/11/2026 |
| Quem fez | Ana (atendimento) |
| Tipo | Prompt |
| O que mudou | "Responda em até 3 frases" → "Responda de forma bem completa" |
| Motivo | Clientes acharam as respostas secas |
| Link do pull request | #12 |
| Resultado dos testes antes | 94% |
| Resultado dos testes depois | 82% |
| Casos que mudaram de resultado | F08, R06, M01, M03 (passaram a ter mais de 3 frases) |
| Novos casos adicionados ao golden | F09: "Resposta é calorosa (juiz)" |
| Aprovado por | — |
| Decisão | **Ajustar**: trocar por "Responda de forma calorosa, em até 3 frases" e rodar de novo |

## Histórico

| Data | Quem | Tipo | Resumo | Testes (antes → depois) | Aprovado por |
|---|---|---|---|---|---|
| | | | | | |
