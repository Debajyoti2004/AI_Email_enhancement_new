from langgraph.graph import START, StateGraph, END
from .build_state import (
  generate_email, 
  Email_Type_Router,
  AgentState
)

# Global variable to store compiled generate agent workflow
compiled_generate_agent_graph = None

def compile_generate_agent():
    global compiled_generate_agent_graph

    if compiled_generate_agent_graph is not None:
        print("Composer agent workflow already compiled. Returning existing instance.")
        return compiled_generate_agent_graph

    print("Compiling composer agent workflow...")
    workflow = StateGraph(AgentState)

    nodes = {
        "Email Type Router": Email_Type_Router,
        "Generation Node": generate_email,
    }

    for name, func in nodes.items():
        workflow.add_node(name, func)

    workflow.add_edge(START, "Email Type Router")
    workflow.add_edge("Email Type Router", "Generation Node")
    workflow.add_edge("Generation Node", END)

    compiled_generate_agent_graph = workflow.compile()
    return compiled_generate_agent_graph





