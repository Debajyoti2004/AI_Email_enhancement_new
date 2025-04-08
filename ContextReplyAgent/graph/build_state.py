import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ContextGenerator import context_reply_chain
from typing_extensions import TypedDict
from Classifier import email_classifier_chain
import json

class AgentState(TypedDict):
    """Agent state representation."""
    email:dict[str,str]
    query:str
    previous_response:str
    generate_email:dict[str,str]
    context:list[str]
    email_type:str

def email_classifier_state(state:AgentState)->AgentState:
    """Classifier function to classify the email."""
    email = state["email"]
    
    response = email_classifier_chain.invoke({
        "email_input":email
    })
    result = response.additional_kwargs["tool_calls"][0]["function"]["arguments"]
    result = json.loads(result)
    email_type = result["email_tone"]
    
    return {
        **state,
        "email_type": email_type
    }

    
def reply_generator_state(state:AgentState)->AgentState:
    """Generator function to reply based on previous response the email."""
    email = state["email"]
    query = state["query"]
    previous_response = state["previous_response"]
    context = state["context"]
    email_type=state["email_type"]

    response = context_reply_chain.invoke({
        "previous_response":previous_response,
        "email_input":email,
        "query":query,
        "context":context,
        "email_type":email_type
    })

    return {
        **state,
        "generate_email":response
    }
