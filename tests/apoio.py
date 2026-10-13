"""Respostas fixas SOMENTE para testes; MCP, grafo e SQLite continuam reais.

Segue a estratégia de conferir.py do professor. Não é um provedor da aplicação.
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PROVEDOR'] = 'openai'
os.environ['OPENAI_API_KEY'] = 'sk-teste-sem-llm'
os.environ['FERIADOS_OFFLINE'] = '1'


def preparar_grafo():
    import conferir
    import etapa07_grafo as g
    from etapa02_extracao import Pedido

    def caso(texto):
        return next((n.split('_')[0] for n, c in conferir.CASOS.items() if c['pedido'] in texto), '?')

    def extrair(texto):
        p = conferir.PEDIDOS_FIXOS.get(caso(texto), conferir.PEDIDOS_FIXOS['C5'])
        return Pedido(**p)

    def rodar(agente, entrada, **kwargs):
        # O redator lê os fatos fornecidos pelo próprio nó, sem chamar um modelo.
        if agente.name == 'Redator':
            import re
            matricula = re.search(r"'matricula': '([0-9]+)'", entrada)[1]
            inicio = re.search(r"'data_inicio': '([0-9-]+)'", entrada)[1]
            fim = re.search(r"'data_fim': '([0-9-]+)'", entrada)[1]
            decisao = 'indeferido' if '"decisao": "indeferido"' in entrada else 'deferido'
            saida = f'Matrícula {matricula}, período {inicio} a {fim}. Decisão: {decisao}.'
        else:
            saida = f'Parecer fixo de {agente.name}; sem LLM.'
        return SimpleNamespace(final_output=saida, context_wrapper=SimpleNamespace(usage=SimpleNamespace(total_tokens=0)))

    patches = [patch.object(g, 'extrair', extrair),
               patch.object(g, 'nota_escopo', lambda t: (conferir.NOTAS_FIXAS.get(caso(t), .05), 'fixo')),
               patch.object(g, 'rodar_com_limites_sync', rodar)]
    for p in patches:
        p.start()
    return g, patches


if __name__ == '__main__':
    os.environ['RH_SAIDAS'] = sys.argv[2]
    g, patches = preparar_grafo()
    from langgraph.checkpoint.sqlite import SqliteSaver
    from dados.casos import CASOS
    from dados_rh import SAIDAS
    with SqliteSaver.from_conn_string(str(SAIDAS / 'persistencia.db')) as cp:
        app = g.construir(cp)
        nome = 'C2_ferias_com_venda'
        if sys.argv[1] == 'iniciar':
            estado = app.invoke({'thread_id': nome, 'texto': CASOS[nome]['pedido']}, g.config_de(nome))
            assert app.get_state(g.config_de(nome)).next == ('aprovacao_chefia',)
            assert not (SAIDAS / 'registros.json').exists()
            print('PAUSADO: checkpoint salvo, sem gravação')
        else:
            g.retomar(app, nome, 'sim', '1010')
            estado = app.get_state(g.config_de(nome)).values
            assert estado['resultado'] == 'registrado', estado
            print('RETOMADO EM OUTRO PROCESSO: registrado b7b6f485')
