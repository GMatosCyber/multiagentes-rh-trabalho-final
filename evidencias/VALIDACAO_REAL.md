# Validação real - OpenAI gpt-4o-mini

Concluída em 13/10/2026, com dados fictícios e aprovações humanas simuladas para o teste.

| Evidência final | Conteúdo |
|---|---|
| [ambiente_llm.txt](ambiente_llm.txt) | conexão real ao modelo, bibliotecas e MCP |
| [conferir_llm_final.txt](conferir_llm_final.txt) | etapas 0-11 e opcionais aprovados pelo verificador |
| [grafo_llm_validado.txt](grafo_llm_validado.txt) | execução dos 12 casos com LLM real |
| [chefia_c2_revisao_llm_validada.txt](chefia_c2_revisao_llm_validada.txt) | rejeição, revisão com feedback e nova pausa |
| [chefia_c2_aprovacao_llm_validada.txt](chefia_c2_aprovacao_llm_validada.txt) | aprovação pela 1010 em outro processo |
| [chefia_c11_aprovacao_llm_validada.txt](chefia_c11_aprovacao_llm_validada.txt) | aprovação pela 1011 em outro processo |
| [casos_llm.json](casos_llm.json) | estados finais, caminhos, protocolos, notas e métricas |
| [observabilidade_llm.json](observabilidade_llm.json) | tempo e tokens reais do C2 |
| [votacao_llm.json](votacao_llm.json) | votos reais e paralelo versus sequência |
| [governanca_llm.txt](governanca_llm.txt) | tentativa real de tool não permitida e orçamento |
| [triagem_llm.json](triagem_llm.json) | C10 com atendente: sim e não |
| [testes_integracao.txt](testes_integracao.txt) | 13 testes adicionais de regressão/integração |

Checkpoints/registros da execução final: `../saidas_validacao_real_finalizada/`.
Não há aprovação pendente ao final dessa demonstração.

O verificador usa LLM real nas etapas 1/2/3/6 com `--llm`; as conferências estruturais
do grafo usam fixtures, conforme o código original do professor. A demonstração dos
12 casos e dos opcionais reais acima complementa essa cobertura, sem mocks.

Arquivos das outras tentativas (`grafo_llm.txt`, `_final`, `_entrega`, `_confirmado`,
`conferir_llm.txt` e retomadas sem `_validada`) são histórico de diagnóstico e podem
conter falhas anteriores às correções. Use os arquivos desta tabela como resultado final.
