# Assistente de Gestão de Pessoas

Trabalho final da aula 10 da disciplina de Multiagentes para Segurança Pública.
Aluno: Guilherme Batista de Castro Matos.

Implementação baseada no material de Francisco Molina Jr., com OpenAI Agents SDK,
MCP, LangGraph e checkpoints SQLite. Dados e normas fictícios, para uso educacional.

## Executar no Windows

Use Python 3.12. Na pasta do repositório, abra o PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$py = '.\.venv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
Copy-Item .env.example .env
```

Configure o `.env` local com seu provedor e sua chave. O arquivo de configuração
e as credenciais não estão publicados. O guia PDF de colegas considera uma cópia
privada já configurada; ao usar este repositório, faça essa configuração primeiro.

### Testes sem chamadas ao modelo

```powershell
& $py conferir.py --opcionais
& $py -m unittest discover -s tests -v
```

### Modelo real e aprovação humana

```powershell
& $py verificar_ambiente.py
$env:RH_SAIDAS = Join-Path (Get-Location) 'saidas_demonstracao'
& $py etapa07_grafo.py --todos
& $py etapa07_grafo.py --pendentes
& $py etapa07_grafo.py --retomar C2_ferias_com_venda "nao:confirme o valor da venda" 1010
& $py etapa07_grafo.py --retomar C2_ferias_com_venda sim 1010
& $py etapa07_grafo.py --retomar C11_diaria_exterior sim 1011
& $py etapa10_observabilidade.py C2_ferias_com_venda
```

As chamadas ao modelo real consomem créditos. Não reinicie o caso nem rode
`--todos` entre a pausa e a retomada. Reenvios de pedidos registrados produzem
`duplicado`, como esperado. O MCP é iniciado automaticamente.

## Entrega e validação

- [Ficha preenchida](docs/Ficha_de_entrega_preenchida.docx)
- [Relatório final](ENTREGA.md)
- [Evidências da validação real](evidencias/VALIDACAO_REAL.md)
- [Verificações complementares da ficha](evidencias/ficha)
- [Guia de teste e apresentação](docs/Guia_teste_e_apresentacao.pdf)
- [Fontes e correspondência com as aulas](FONTES.md)
- [Enunciado original](ENUNCIADO.md)

Etapas 0 a 11 e opcionais A/B/C passaram no verificador. Também foram executados
os 12 casos com OpenAI gpt-4o-mini, MCP e SQLite reais, e 13 testes adicionais.
O verificador estrutural do grafo usa fixtures, conforme o professor; as decisões
humanas das demonstrações foram simuladas. Votação e triagem humana ficam
desligadas por padrão no grafo principal.

O código original e sua autoria estão documentados em FONTES.md. O repositório
não inclui PDFs das aulas, ambiente virtual, credenciais ou bancos locais.
