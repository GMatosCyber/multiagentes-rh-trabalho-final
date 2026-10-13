"""Etapa 10 e bônus B: hooks de observação, permissões e orçamento.
Referências: aula3/agente_hook2.py, agente_hook3.py; aula8/exemplos/06_excessive_agency.
"""
from agents import AgentsException, RunHooks

class LimiteExcedido(AgentsException):
    """Execução fora do orçamento ou das permissões."""

PERMISSOES: dict[str, set[str]] = {
    "Normas": {"consultar_normas"}, "Escala": {"consultar_escala"},
    "Financeiro": {"tabela_diarias", "consultar_remuneracao", "cotacao_dolar"},
    "Coordenador": {"parecer_normas", "parecer_escala", "parecer_financeiro"}, "Redator": set(),
}



class Governanca(RunHooks):
    def __init__(self, max_tools: int = 6, max_llm: int = 12, verbose: bool = True):
        self.max_tools, self.max_llm, self.verbose = max_tools, max_llm, verbose
        self.tools_chamadas = 0
        self.chamadas_llm = 0
        self.eventos: list[dict] = []  # ETAPA 10.1: o que aconteceu, para gravar em saidas/metricas.jsonl

    async def on_tool_start(self, context, agent, tool) -> None:
        self.tools_chamadas += 1
        if tool.name not in PERMISSOES.get(agent.name, set()):
            raise LimiteExcedido(f"{agent.name} não pode usar {tool.name}")
        if self.tools_chamadas > self.max_tools:
            raise LimiteExcedido(f"orçamento de tools estourado ({self.tools_chamadas} de {self.max_tools})")
        if self.verbose:
            print(f"[governança] {agent.name} -> {tool.name}: OK ({self.tools_chamadas} de {self.max_tools})")
        # 🆕 B.2 (opcional) -- levante LimiteExcedido se:
        #   - tool.name não está em PERMISSOES.get(agent.name, set())   -> "Coordenador não pode usar consultar_remuneracao"
        #   - self.tools_chamadas > self.max_tools                       -> "orçamento de tools estourado (N de M)"
        #   Imprima a decisão quando self.verbose (ex.: "[governança] Financeiro -> tabela_diarias: OK").

    async def on_llm_start(self, context, agent, system_prompt, input_items) -> None:
        self.chamadas_llm += 1
        if self.chamadas_llm > self.max_llm:
            raise LimiteExcedido(f"orçamento de LLM estourado ({self.chamadas_llm} de {self.max_llm})")
        # 🆕 B.3 (opcional) -- acima de self.max_llm, levante LimiteExcedido.
        #   (Parece o max_turns da Etapa 4.7, mas a mensagem e o registro são SEUS, e vale para a equipe toda.)

    async def on_tool_end(self, context, agent, tool, result) -> None:
        # ETAPA 10.1 -- acrescente a self.eventos: {"agente", "tool", "argumentos", "resultado" (truncado)}.
        #   Os argumentos estão em context.tool_arguments (texto JSON) quando a tool é uma function_tool.
        self.eventos.append({"agente": agent.name, "tool": tool.name,
                             "argumentos": getattr(context, "tool_arguments", ""),
                             "resultado": str(result)[:500]})

    async def on_agent_end(self, context, agent, output) -> None:
        # ETAPA 10.1 -- acrescente a self.eventos os tokens até aqui: context.usage.total_tokens
        self.eventos.append({"agente": agent.name, "tokens": context.usage.total_tokens})
