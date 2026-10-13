from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
class Sem(TypedDict):
    violacoes: list[str]
class Com(TypedDict):
    violacoes: Annotated[list[str],operator.add]
for cls in [Sem,Com]:
    g=StateGraph(cls)
    g.add_node('normas',lambda s:{'violacoes':['N3']})
    g.add_node('escala',lambda s:{'violacoes':['teste']})
    g.add_edge(START,'normas');g.add_edge(START,'escala')
    g.add_edge('normas',END);g.add_edge('escala',END)
    try: print(cls.__name__,g.compile().invoke({'violacoes':[]}))
    except Exception as e: print(cls.__name__,type(e).__name__,str(e).splitlines()[0])
