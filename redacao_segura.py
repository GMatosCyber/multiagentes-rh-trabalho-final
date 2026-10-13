"""A autorização N8 é declarada pelo código, sem depender da interpretação do Redator."""
import re

from etapa06_regras import precisa_chefia


def status_autorizacao(estado: dict) -> str:
    if estado.get('aprovado'):
        return f"Autorização (N8): ratificado pela chefia {estado['aprovador']}."
    if precisa_chefia(estado['pedido'], estado.get('violacoes', [])):
        return 'Autorização (N8): minuta de deferimento; aguarda aprovação da chefia imediata.'
    if estado.get('decisao') == 'deferido':
        return 'Autorização (N8): abono deferido automaticamente, sem necessidade de chefia.'
    return 'Autorização (N8): indeferimento por regra objetiva; não exige aprovação da chefia.'


def normalizar_autorizacao(texto: str, estado: dict) -> str:
    # Uma afirmação de autoridade do modelo não é evidência de aprovação.
    # Preserva a fundamentação e os valores; substitui as linhas de autorização pela regra N8.
    linhas = [l for l in texto.splitlines() if not re.search(
        r'chefia|pagamento|aprova(?:do|da|ção|cao)', l, re.IGNORECASE)]
    corpo = '\n'.join(linhas).strip()
    if not corpo:
        p = estado['pedido']
        corpo = f"Matrícula {p['matricula']}. Período {p['data_inicio']} a {p['data_fim']}. Decisão: {estado['decisao']}."
    return corpo + '\n\n' + status_autorizacao(estado)
