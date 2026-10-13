"""
ETAPA 10 -- Observabilidade (15 min): onde o tempo foi gasto e quanto custou, por nó do grafo.

ESQUELETO:
  ETAPA 10.2 -- medido(): embrulha um nó, mede o tempo e grava uma linha em saidas/metricas.jsonl
  (PRONTO)   -- resumo(): nós percorridos, tempo total, nó mais lento e tokens totais de uma execução
  (ETAPA 10.1 fica em etapa10_governanca.py: o hook do 🆕 B ganha um segundo papel, registrar)

Até você fazer a 10.2, medido() devolve o nó sem mudar nada: o grafo funciona igual.

REFERÊNCIAS NAS AULAS
  aula5/exemplos/11_observabilidade/agente_observavel.py        ler o que aconteceu numa execução (result.new_items)
  aula3/agente_hook2.py, aula3/agente_hook3.py                  RunHooks para enxergar o loop do agente
  aula8/exemplos/03_observabilidade/1_codigo_pronto/passo1_trace.py   trace e spans (o Langfuse do passo 2 é opcional)

Rodar:
    python etapa10_observabilidade.py <thread_id>     # imprime o resumo de uma execução já feita
"""
import functools
import json
import sys
import time

from dados_rh import SAIDAS
from metricas_llm import USO
from threading import Lock

ARQUIVO_METRICAS = SAIDAS / "metricas.jsonl"
_LOCK = Lock()


def medido(nome: str, no):
    # ETAPA 10.2 -- devolva uma função que:
    #   1. mede o tempo de no(estado) com time.perf_counter();
    #   2. grava em ARQUIVO_METRICAS uma linha JSON com: thread_id (estado.get("thread_id")), no, segundos,
    #      e, se o nó devolveu, "tokens" e "fonte_feriados";
    #   3. devolve o MESMO dicionário que o nó devolveu.
    #   Use @functools.wraps(no) para o nome do nó continuar o mesmo.
    @functools.wraps(no)
    def medido_no(estado):
        t0 = time.perf_counter()
        USO.set(0)
        resultado = None
        status = "ok"
        try:
            resultado = no(estado)
            return resultado
        except BaseException as erro:
            status = "pausado" if type(erro).__name__ == "GraphInterrupt" else "erro"
            raise
        finally:
            linha = {"thread_id": estado.get("thread_id", ""), "no": nome,
                     "segundos": round(time.perf_counter() - t0, 6), "status": status}
            if resultado:
                if USO.get():
                    linha["tokens"] = USO.get()
                for campo in ("tokens", "fonte_feriados"):
                    if campo in resultado:
                        linha[campo] = resultado[campo]
            with _LOCK:
                with open(ARQUIVO_METRICAS, "a", encoding="utf-8") as arquivo:
                    arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return medido_no


def resumo(thread_id: str) -> dict:
    """(PRONTO) Junta as linhas de ARQUIVO_METRICAS de uma execução. Só funciona depois que o medido() (10.2) grava."""
    if not ARQUIVO_METRICAS.exists():
        return {"erro": "saidas/metricas.jsonl ainda não existe: faça a ETAPA 10.2 e rode o grafo"}
    linhas = [json.loads(l) for l in ARQUIVO_METRICAS.read_text(encoding="utf-8").splitlines() if l.strip()]
    linhas = [l for l in linhas if l.get("thread_id") == thread_id]
    if not linhas:
        return {"erro": f"nenhuma métrica com thread_id={thread_id!r}"}
    lento = max(linhas, key=lambda l: l.get("segundos", 0))
    return {"nos": [l.get("no") for l in linhas],
            "segundos_total": round(sum(l.get("segundos", 0) for l in linhas), 2),
            "mais_lento": (lento.get("no"), lento.get("segundos")),
            "tokens_total": sum(l.get("tokens", 0) or 0 for l in linhas)}


if __name__ == "__main__":
    print(json.dumps(resumo(sys.argv[1]), ensure_ascii=False, indent=2))
