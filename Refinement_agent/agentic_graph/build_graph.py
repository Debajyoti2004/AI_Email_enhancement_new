from .build_state import (
    AgentState,
    refinement_grader, 
    user_friendly_generator
)
from langgraph.graph import START, StateGraph, END

# Global variable to store the compiled refinement agent workflow
compiled_refinement_agent_graph = None

def compile_refinement_agent():
    global compiled_refinement_agent_graph

    if compiled_refinement_agent_graph is not None:
        print("Refinement agent workflow already compiled. Returning existing instance.")
        return compiled_refinement_agent_graph

    print("Compiling refinement agent workflow...")
    workflow = StateGraph(AgentState)

    nodes = {
        "Refinement Grader": refinement_grader,
        "Refined Email Generate": user_friendly_generator
    }

    for name, func in nodes.items():
        workflow.add_node(name, func)

    workflow.add_edge(START, "Refinement Grader")
    workflow.add_edge("Refinement Grader", "Refined Email Generate")
    workflow.add_edge("Refined Email Generate", END)

    compiled_refinement_agent_graph = workflow.compile()
    return compiled_refinement_agent_graph
