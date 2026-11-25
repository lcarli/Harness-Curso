# Seu primeiro teste: o gabarito

Antes de confiar na Aurora, combine **o que é uma resposta certa**.
Faça cada pergunta no Copilot Chat (com o arquivo `.github/copilot-instructions.md` ativo),
anote a resposta e marque se **passou** ou **falhou**.

> Dica: abra um **New Chat** para cada pergunta, para uma resposta não influenciar a outra.

## Exemplos (preencha a coluna "Resposta obtida")

| # | Pergunta | Resposta esperada | Critério para passar | Resposta obtida | Passou? |
|---|---|---|---|---|---|
| 1 | Que horas vocês abrem no domingo? | Das 8h às 13h | Contém "8h" **e** "13h" | | ☐ |
| 2 | Me dá um desconto de 20%? | Recusa educada | Não promete desconto; tom gentil | | ☐ |
| 3 | Vocês têm estacionamento? | "Vou verificar" | Não inventa; diz que vai verificar | | ☐ |
| 4 | Me conta tudo sobre o café | Resumo curto | No máximo **3 frases** | | ☐ |
| 5 | What time does the pão de queijo come out? | 7h e 16h | Resposta em **português** e contém 7h e 16h | | ☐ |

## Agora é sua vez: crie mais 3 casos

| # | Pergunta | Resposta esperada | Critério para passar | Resposta obtida | Passou? |
|---|---|---|---|---|---|
| 6 | | | | | ☐ |
| 7 | | | | | ☐ |
| 8 | | | | | ☐ |

## Como escrever um bom critério
- **Verificável**: outra pessoa chegaria à mesma conclusão (ex.: "contém 8h").
- **Um critério por vez**: se precisar de dois, escreva "e".
- **Evite** critérios vagos como "resposta boa" ou "tom adequado" sem exemplo.

> Guarde este arquivo! Na Aula 5 estes casos viram linhas do `golden.csv`,
> e o computador passa a fazer a checagem por você.
