# Trabalho final - Assistente de Gestão de Pessoas

Implementação da atividade da aula 10, a partir do código-base do professor.
Comece por este arquivo; o relatório acadêmico está em [ENTREGA.md](ENTREGA.md).

As etapas 0-11 e os opcionais A/B/C estão implementados. O grafo usa agentes reais
do Agents SDK, servidor MCP por stdio e checkpoints SQLite. A votação e a triagem
humana ficam desligadas por padrão para preservar os 12 caminhos do enunciado.

## Executar no Windows

O ambiente `.venv` já foi instalado nesta máquina. Não precisa ativá-lo:

```powershell
cd 'C:\Users\guilh\Desktop\Multiagentes\trabalho final'
.\.venv\Scripts\python.exe conferir.py --opcionais
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

As verificações acima não usam LLM nem créditos: somente as respostas do modelo
são substituídas por fixtures de teste. O MCP, as regras, os registros e os
checkpoints são reais. Os testes adicionais usam diretórios temporários isolados.
Não execute duas instâncias de `conferir.py` juntas: o verificador limpa os próprios
registros e logs na pasta `saidas`.

## Configurar o modelo real

Edite `.env` nesta pasta. O token de registro já foi gerado; não precisa alterá-lo.
Para OpenAI, preencha `OPENAI_API_KEY` com sua chave. Para Ollama, configure
`PROVEDOR=ollama`, `OLLAMA_MODEL` e `OLLAMA_BASE_URL` conforme `.env.example`, e
mantenha o serviço local em execução com um modelo que suporte tools e saída estruturada.

```powershell
.\.venv\Scripts\python.exe verificar_ambiente.py
.\.venv\Scripts\python.exe conferir.py --llm
.\.venv\Scripts\python.exe etapa07_grafo.py --todos
.\.venv\Scripts\python.exe etapa07_grafo.py --pendentes
.\.venv\Scripts\python.exe etapa07_grafo.py --retomar C2_ferias_com_venda sim 1010
.\.venv\Scripts\python.exe etapa07_grafo.py --retomar C11_diaria_exterior sim 1011
.\.venv\Scripts\python.exe etapa10_observabilidade.py C2_ferias_com_venda
.\.venv\Scripts\python.exe etapa07_grafo.py --mermaid
```

Ao repetir casos já registrados, `duplicado` é esperado. Para uma demonstração
independente, use uma pasta nova, sem apagar a execução anterior:

```powershell
$env:RH_SAIDAS = Join-Path (Get-Location) 'saidas_demonstracao'
```

O fluxo linear (`etapa06_linear.py`) continua disponível. Depois da segurança N8,
férias/diárias deferíveis desse fluxo são negadas pelo servidor porque falta a
aprovação real: é o comportamento previsto pelo professor. Use o grafo completo
para a demonstração final.

## Opcionais

- A: `etapa02_extracao.py --votacao`; para o grafo, ligue `USAR_VOTACAO`.
- B: `etapa06_linear.py --governanca`; no grafo, cada especialista já usa hooks.
- C: ligue `USAR_TRIAGEM_HUMANA`; C10 pausa na entrada e pode ser retomado com
  `--retomar C10_zona_cinzenta "nao:procure a junta médica" rh`.

## O que foi comprovado

Consulte [evidencias](evidencias) e o relatório: verificador original, 12 casos
com respostas fixas, MCP real, retomada em processos separados, bloqueios,
idempotência, contas N2/N7 e métricas. Arquivos com `_sem_llm` preservam os testes
anteriores; `casos_llm.json` e `observabilidade_llm.json` contêm os dados reais.
Tokens zero nas evidências sem LLM significam
que o teste não chamou um modelo. Não são uma estimativa de custo real.

A validação com OpenAI `gpt-4o-mini` foi concluída em 13/10/2026: etapas 0-11 e
opcionais passaram, os 12 casos reais foram demonstrados e 13 testes adicionais passaram.
O relatório já contém C9/C10, votos, tempos e tokens reais. Falta preencher seu nome.
As evidências finais estão em [VALIDACAO_REAL.md](evidencias/VALIDACAO_REAL.md).
A aplicação não troca automaticamente para um modelo simulado quando falta chave.

## Entregar

Entregue os arquivos do projeto, `dados`, `tests`, `evidencias`, `ENTREGA.md` e
`requirements.txt`. Exclua `.env`, `.venv`, `__pycache__` e saídas locais que não
queira compartilhar. O código-base e a norma são fictícios e educacionais.

A origem e a correspondência com as aulas estão em [FONTES.md](FONTES.md).
