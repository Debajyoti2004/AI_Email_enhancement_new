from .build_state import reply_generator_state,email_classifier_state,AgentState
from langgraph.graph import START, StateGraph, END

# Global variable to store compiled reply agent workflow
compiled_reply_agent_graph = None

def compile_reply_agent():
    global compiled_reply_agent_graph

    if compiled_reply_agent_graph is not None:
        print("Reply agent workflow already compiled. Returning existing instance.")
        return compiled_reply_agent_graph

    print("Compiling reply agent workflow...")
    workflow = StateGraph(AgentState)

    workflow.add_node("Context Reply Agent", reply_generator_state)
    workflow.add_node("Email Classifier", email_classifier_state)
    workflow.add_edge(START, "Email Classifier")
    workflow.add_edge("Email Classifier", "Context Reply Agent")
    workflow.add_edge("Context Reply Agent", END)

    compiled_reply_agent_graph = workflow.compile()
    return compiled_reply_agent_graph
