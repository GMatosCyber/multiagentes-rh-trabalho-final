"""Coleta evidências usando o provedor real configurado em .env, sem mocks.

Uso: python validar_modelo_real.py coletar | votacao | triagem
Para os 12 casos, execute primeiro etapa07_grafo.py --todos e as retomadas.
"""
import asyncio
import json
import sys
import time
from pathlib import Path

from dados.casos import CASOS
from dados_rh import PASTA, SAIDAS
from etapa02_extracao import INSTRUCOES_VOTANTES, criar_extrator, extrair_com_votacao
from etapa04_ferramentas import rodar_com_limites_sync
from etapa10_observabilidade import resumo
from langgraph.checkpoint.sqlite import SqliteSaver
import etapa07_grafo as grafo

EVIDENCIAS = PASTA / 'evidencias'


def salvar(nome, dados):
    EVIDENCIAS.mkdir(exist_ok=True)
    (EVIDENCIAS / nome).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')


def snapshot(estado):
    return {k: estado.get(k) for k in (
        'caminho', 'resultado', 'protocolo', 'decisao', 'pedido', 'despacho', 'nota_escopo',
        'violacoes', 'contas_financeiras', 'alternativa_periodo', 'tentativas', 'rejeicoes', 'feedback_chefia')}


def coletar():
    casos = {}
    with SqliteSaver.from_conn_string(str(SAIDAS / 'checkpoints.db')) as cp:
        app = grafo.construir(cp)
        for nome in CASOS:
            estado = app.get_state(grafo.config_de(nome))
            casos[nome] = {**snapshot(estado.values), 'proximo': list(estado.next), 'metricas': resumo(nome)}
    salvar('casos_llm.json', {'modelo': grafo.MODELO, 'casos': casos})
    salvar('observabilidade_llm.json', resumo('C2_ferias_com_venda'))
    for nome, estado in casos.items():
        print(nome, estado['resultado'], estado['protocolo'], 'tokens=',estado['metricas'].get('tokens_total'))


def votacao():
    casos = {}
    for nome in ('C1_abono_simples', 'C2_ferias_com_venda', 'C9_divergencia'):
        t0 = time.perf_counter()
        pedido, divergencia, votos = asyncio.run(extrair_com_votacao(CASOS[nome]['pedido']))
        casos[nome] = {'segundos_paralelo': round(time.perf_counter()-t0,3), 'tokens_paralelo': pedido._tokens,
                       'divergencia': divergencia, 'pedido': pedido.model_dump(mode='json'),
                       'votos': [v.model_dump(mode='json') for v in votos]}
        print(nome, 'divergencia=', divergencia, 'segundos=', casos[nome]['segundos_paralelo'])
    t0 = time.perf_counter()
    tokens = 0
    for instrucoes in INSTRUCOES_VOTANTES:
        r = rodar_com_limites_sync(criar_extrator(instrucoes), CASOS['C2_ferias_com_venda']['pedido'])
        tokens += r.context_wrapper.usage.total_tokens
    casos['C2_sequencial'] = {'segundos':round(time.perf_counter()-t0,3),'tokens':tokens}
    salvar('votacao_llm.json', {'modelo':grafo.MODELO,'casos':casos})


def triagem():
    grafo.USAR_TRIAGEM_HUMANA = True
    resultados = {}
    with SqliteSaver.from_conn_string(str(SAIDAS / 'triagem.db')) as cp:
        app = grafo.construir(cp)
        for escolha in ('nao:procure a junta médica ou licença para acompanhar familiar', 'sim:tratar como abono'):
            thread = 'triagem_real_' + escolha.split(':')[0]
            app.checkpointer.delete_thread(thread)
            estado = app.invoke({'thread_id':thread, 'texto':CASOS['C10_zona_cinzenta']['pedido']},grafo.config_de(thread))
            assert app.get_state(grafo.config_de(thread)).next == ('triagem_humana',), 'C10 não pausou na triagem'
            nota = estado['nota_escopo']
            grafo.retomar(app,thread,escolha,'rh')
            estado = app.get_state(grafo.config_de(thread))
            resultados[thread] = {**snapshot(estado.values),'nota_escopo_antes':nota,'proximo':list(estado.next)}
    salvar('triagem_llm.json', {'modelo':grafo.MODELO,'casos':resultados})


if __name__ == '__main__':
    {'coletar':coletar,'votacao':votacao,'triagem':triagem}[sys.argv[1]]()
