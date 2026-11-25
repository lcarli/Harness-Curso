# Aula 3 — Agentes

- `.github/agents/aurora-gerente.agent.md` — agente personalizado do Copilot (abra **esta pasta** `aula3/` no VS Code para o Copilot encontrá-lo).
- `agente_aurora.py` — agente em Python: modelo + ferramentas + loop. Rode com `python aula3/agente_aurora.py`.
- `dados/` — estoque e vendas fictícios. As encomendas confirmadas vão para `dados/encomendas.txt`.

> **Atenção:** o suporte a ferramentas (*tool calling*) **varia por provedor e por modelo**.
> Consulte a documentação do seu provedor. Se receber erro 400 mencionando `tools`,
> troque por um modelo que suporte ferramentas. No Ollama, escolha um modelo marcado com suporte a "tools".
> Sem acesso? Cole o arquivo no Copilot Chat e peça: *"simule este agente para a pergunta 'Dá para atender 30 pessoas amanhã?' mostrando cada passo"*.
