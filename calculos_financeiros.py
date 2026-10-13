"""Contas N2/N7 em Python; o Financeiro explica os resultados, sem decidir valores."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date


def dinheiro(valor):
    return float(Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def venda(dias: int, salario_base: float) -> float:
    if not 0 <= dias <= 10 or salario_base < 0:
        raise ValueError('Dias vendidos ou remuneração inválidos')
    return dinheiro(Decimal(dias) * Decimal(str(salario_base)) / Decimal(30))


def diarias(inicio: str, fim: str, valor_diaria: float, moeda: str, cotacao=None) -> dict:
    pernoites = (date.fromisoformat(fim) - date.fromisoformat(inicio)).days
    if pernoites < 0 or valor_diaria < 0:
        raise ValueError('Período ou valor da diária inválido')
    quantidade = Decimal(pernoites) + Decimal('0.5')
    total = quantidade * Decimal(str(valor_diaria))
    return {'pernoites': pernoites, 'quantidade_diarias': float(quantidade), 'moeda': moeda,
            'total': dinheiro(total), 'cotacao': cotacao,
            'total_brl': dinheiro(total * Decimal(str(cotacao))) if moeda == 'USD' and cotacao else
                         dinheiro(total) if moeda == 'BRL' else None}


def fatos_financeiros(pedido: dict) -> dict:
    # Somente esta rotina do papel Financeiro consulta a remuneração. Nunca a devolve.
    from etapa05_cliente_mcp import chamar_mcp
    from etapa04_ferramentas import cotacao_usd_brl
    tipo = pedido['tipo']
    if tipo == 'ferias' and pedido.get('dias_vendidos', 0):
        remuneracao = chamar_mcp('consultar_remuneracao', {'matricula': pedido['matricula']})
        return {'regra': 'N2', 'dias_vendidos': pedido['dias_vendidos'],
                'venda_total_brl': venda(pedido['dias_vendidos'], remuneracao['salario_base'])}
    if tipo == 'diaria':
        tabela = chamar_mcp('tabela_diarias', {'tipo_destino': pedido['tipo_destino']})
        cotacao = cotacao_usd_brl() if tabela['moeda'] == 'USD' else None
        return {'regra': 'N7', **diarias(pedido['data_inicio'], pedido['data_fim'],
                                       tabela['valor_diaria'], tabela['moeda'], cotacao)}
    return {'regra': None, 'observacao': 'não se aplica'}
