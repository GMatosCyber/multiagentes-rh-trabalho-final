"""Uso por chamada sem compartilhar contadores entre os ramos paralelos."""
from contextvars import ContextVar

USO = ContextVar("tokens_llm", default=0)


def registrar_uso(resultados):
    USO.set(sum(getattr(getattr(getattr(r, "context_wrapper", None), "usage", None),
                        "total_tokens", 0) for r in resultados))
