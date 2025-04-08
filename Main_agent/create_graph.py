from .create_state import GraphState,triage_router,decide_to_triage,response_rag_agent_state,ignore_state
from langgraph.graph import StateGraph, START, END

# Global variable to hold the compiled graph
compiled_main_agent_graph = None

def compile_main_agent_graph():
    global compiled_main_agent_graph

    if compiled_main_agent_graph is not None:
        print("Workflow already compiled. Returning existing instance.")
        return compiled_main_agent_graph

    print("Compiling workflow...")
    builder = StateGraph(GraphState)

    # Define nodes
    builder.add_node("triage_router", triage_router)
    builder.add_node("response_rag_agent", response_rag_agent_state)
    # builder.add_node("notify_state", notify_state)
    builder.add_node("ignore_state", ignore_state)

    # Define edges
    builder.add_edge(START, "triage_router")
    builder.add_conditional_edges(
        "triage_router",
        decide_to_triage,
        {
            "response-agent": "response_rag_agent",
            "end": "ignore_state"
        }
    )
    builder.add_edge("response_rag_agent", END)
    builder.add_edge("ignore_state", END)

    compiled_main_agent_graph = builder.compile()
    return compiled_main_agent_graph
 