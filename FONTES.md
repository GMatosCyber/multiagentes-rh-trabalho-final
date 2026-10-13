# Fontes e decisões de implementação

O PDF da aula 1 identifica o professor como **Francisco Molina Jr.** O slide 4 da
aula 7 contém o link que permitiu identificar o repositório:
[franciscomduarte/material-pcdf](https://github.com/franciscomduarte/material-pcdf).

Foi consultado o commit `0203c324f544a9bb541679356f6bf86bd4c1c034`, obtido em
13/10/2026. A pasta `aula10` desse commit forneceu enunciado, roteiro, dados,
código-base e verificador. Somente essa atividade foi copiada para o projeto.
`conferir.py`, o enunciado, o roteiro e os dados de exemplo foram preservados.

## Material disponível

| Material | Conteúdo aplicado |
|---|---|
| Aula 01: PDF e PPTX | ementa, Agent/Runner, tools, output_type, memória, guardrails e limites |
| Aula 03: PDF e PPTX | hooks, turnos, timeout, retry, hash e freio humano |
| Aula 04: arquivo supplementary ZIP, com PDF/PPTX | handoffs, as_tool, comunicação e contratos |
| Aula 05: supplementary sem extensão, que é PDF | MCP, descoberta de tools, integração e segurança |
| Aula 05 - Complemento | autorização, privilégio mínimo, filtros de tools e HTTP |
| Aula 06 e Complemento | estado, roteadores, fan-out/fan-in, ciclos e nós de LLM/MCP/API |
| Aula 07 | equipe de agentes, SQLite, interrupt, retomada e revisão |
| Aula 08 | observabilidade, guardrails, excessive agency, autorização e integração |
| Aula 10 | assistente RH; etapas 0-11 e opcionais A/B/C |

Os PDFs com nomes UUID repetem os materiais das aulas 5 e 8. Não havia anexos
separados identificados como aulas 2 e 9. A pasta `aula2` foi consultada no
repositório; o deck da aula 8 também contém referências internas a exemplos e
sessões “aula9”. Não inferi uma atividade adicional a partir dessa numeração.

## Critério adotado

Mantive a arquitetura e os comandos solicitados pelo professor: um arquivo por
etapa, Agents SDK, MCP por stdio, LangGraph, SQLite local e norma fictícia.
Não acrescentei frontend, Docker, banco externo ou funcionalidades fora do trabalho.

A correspondência de cada implementação com os exemplos está na seção final
de `ENTREGA.md` e nos comentários `REFERÊNCIAS NAS AULAS` dos módulos.

Além das lacunas, acrescentei apenas apoio ao exercício: contas N2/N7 com Decimal,
métricas de extração/classificação, bloqueio de despacho inválido após três
tentativas, filtro de leitura do atendente MCP, saídas isoláveis em `RH_SAIDAS`,
testes de integração, evidências e instruções de execução.

O verificador do professor usa respostas LLM fixas por padrão. Os testes adicionais
seguem esse método e usam o MCP real, sem confundir teste estrutural com validação
empírica de prompts. A aplicação principal continua exigindo um provedor real.

## Arquivos de referência

- [Enunciado original](ENUNCIADO.md)
- [Passo a passo original](PASSO_A_PASSO.md)
- [Norma fictícia](dados/normas.md)
- [Relatório de entrega](ENTREGA.md)
- [Instruções desta implementação](INICIAR_AQUI.md)

`requirements.txt` é o arquivo do professor. `requirements-lock.txt` registra as
versões instaladas e testadas neste Windows/Python 3.12. Para reproduzir o ambiente,
instale o lock; para outros sistemas operacionais, use o requirements original.

## Validação com OpenAI em 13/10/2026

Após configurar a chave no `.env`, o modelo `gpt-4o-mini` foi exercitado com o verificador,
os 12 casos, retomadas e opcionais reais. Os defeitos de redação/extração observados levaram
às correções e regressões descritas em `ENTREGA.md`. O status N8 é composto em Python
por `redacao_segura.py`; alternativas N3/N5 são calculadas em `sugestoes_periodo.py`.
As evidências finais estão em `evidencias/VALIDACAO_REAL.md`.
