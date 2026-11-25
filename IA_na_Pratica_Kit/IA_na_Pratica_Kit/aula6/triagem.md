# Triagem de falhas: um teste falhou. E agora?

Calma: uma falha é **informação**, não um desastre. Siga as perguntas na ordem.

```
Um caso FALHOU
   │
   ├─ 1. É uma falha NOVA? (passava antes desta mudança?)
   │      └─ Não, já falhava antes → registre como conhecida e trate separadamente.
   │
   ├─ 2. É variação aleatória? Rode o mesmo caso 3 vezes.
   │      ├─ Passou 2 ou 3 vezes → instabilidade: deixe o prompt mais explícito
   │      │                        ou reduza a temperatura. Anote.
   │      └─ Falhou 2 ou 3 vezes → é real. Continue.
   │
   └─ 3. Onde está o problema?
          ├─ No PROMPT?      A regra está escrita? Está clara? Duas regras brigam?
          ├─ Nos DADOS?      A informação existe no manual/CSV? Está correta e atualizada?
          ├─ Na FERRAMENTA?  O agente chamou a ferramenta certa? A busca trouxe o trecho certo?
          └─ No TESTE?       O critério está errado ou rígido demais? (ex.: exige "8h" e a
                             resposta disse "8 horas" — a resposta está certa, o teste não)
```

## Tabela de triagem (preencha uma linha por falha)

| Caso | Nova? (s/n) | Passou em 3 tentativas? (0–3) | Onde está o problema (prompt / dados / ferramenta / teste) | Ação | Responsável |
|---|---|---|---|---|---|
| | | | | | |

## Dicas
- **Nunca** "conserte" um teste só para ele passar. Primeiro pergunte: *a resposta estava certa?*
- Se o teste estava errado, corrija o teste **e registre** em `mudancas.md`.
- Falhas de **segurança e privacidade** não entram na conta de "variação aleatória": uma vez já é demais. Corrija antes de publicar.
- Toda falha real encontrada no uso vira **um novo caso** no `golden.csv`.
