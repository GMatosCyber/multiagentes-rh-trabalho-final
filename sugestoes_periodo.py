"""Alternativas de datas verificadas em Python, para violações N3/N5."""
from datetime import date, timedelta

from etapa04_ferramentas import eh_dia_util, inicio_permitido


def sugerir_periodo(pedido: dict, escala: dict, violacoes: list[str]) -> dict | None:
    if not any(v.startswith(('N3:', 'N5:')) for v in violacoes):
        return None
    if pedido['tipo'] not in {'ferias', 'abono'}:
        return None
    inicio = date.fromisoformat(pedido['data_inicio'])
    duracao = (date.fromisoformat(pedido['data_fim']) - inicio).days + 1
    afastamentos = [a for a in escala.get('afastamentos', []) if a['matricula'] != pedido['matricula']]
    limite = escala.get('limite_afastados', 1)
    if any(v.startswith('N5:') for v in violacoes) and afastamentos:
        inicio = max(inicio, max(date.fromisoformat(a['fim']) for a in afastamentos) + timedelta(days=1))
    for deslocamento in range(90):
        candidato = inicio + timedelta(days=deslocamento)
        fim = candidato + timedelta(days=duracao - 1)
        permitido = inicio_permitido(candidato.isoformat()) if pedido['tipo'] == 'ferias' else eh_dia_util(candidato)
        sobrepostos = sum(a['inicio'] <= fim.isoformat() and candidato.isoformat() <= a['fim'] for a in afastamentos)
        if permitido and sobrepostos < limite:
            return {'data_inicio': candidato.isoformat(), 'data_fim': fim.isoformat(), 'dias_corridos': duracao}
    return None
