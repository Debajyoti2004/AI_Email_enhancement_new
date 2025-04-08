import json
from langchain_cohere import ChatCohere
from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from CreateTools import  tools, tools_by_name, search_recall_memories
from CreatePrompt import prompt
from langchain.schema import Document
from langchain_core.messages.utils import get_buffer_string  
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import streamlit as st
import requests
from langgraph.graph import END
import tiktoken
import os
from dotenv import load_dotenv
load_dotenv()

llm_model = ChatCohere(
    cohere_api_key=os.getenv("MAIN_COHERE_API_KEY"),
    temperature=0
).bind_tools(
    tools=tools
)

tokenizer = tiktoken.get_encoding("cl100k_base")

class AgentState(TypedDict):
    recall_memories: List[str]
    messages: Annotated[Sequence[BaseMessage], add_messages]


def tool_node(state: AgentState):
    outputs = []
    last_message = state["messages"][-1]
    print(f"last_message:{last_message}")
    if hasattr(last_message, "tool_calls"):
        for tool_call in last_message.tool_calls:

            # print(tool_call["name"])
            # print(tools_by_name.keys())
            # print(tool_call["args"])
            # print("Tool Object:", tools_by_name["model_generation"])
            # print("Has Invoke Method:", hasattr(tools_by_name["model_generation"], "invoke"))
            print("Calling tool:", tool_call["name"])
            print("Tool args:", tool_call["args"])
            print("Expected input schema:", tools_by_name[tool_call["name"]].args_schema)


            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            # print(type(tool_result), tool_result)
            
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call.get("id", ""),
                )
            )
    return {
        **state,
        "messages": outputs
    }

# def tool_node(state: AgentState):
#     outputs = []
#     last_message = state["messages"][-1]
#     print(f"last_message: {last_message}")
    
#     if "tool_calls" in last_message:
#         for tool_call in last_message["tool_calls"]:
#             last_tool = tool_call["name"]
#             last_tool_args = tool_call["args"]

#             tool_result = tools_by_name[last_tool].invoke(last_tool_args)

#             outputs.append(
#                 ToolMessage(
#                     content=json.dumps(tool_result),
#                     name=last_tool,
#                     tool_call_id=tool_call.get("id", ""),
#                 )
#             )
    
#     return {
#         **state,
#         "messages": outputs
#     }


def agent(state: AgentState,config: RunnableConfig) -> AgentState:
    """Process the current state and generate a response using the LLM."""
    messages = state["messages"]
    recall_str = (
        "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
    )
    prediction = llm_model.invoke(
        [prompt] + messages + [recall_str], config
    )
    return {
        **state,
        "messages": [prediction]
        }

def load_memories(state: AgentState, config: RunnableConfig) -> AgentState:
    """Load relevant memories for the conversation."""
    convo_str = get_buffer_string(state["messages"])
    convo_str = tokenizer.decode(tokenizer.encode(convo_str)[:2048])
    recall_memories = search_recall_memories.invoke({"comb_str": convo_str, "config": config})
    return {
        **state,
        "recall_memories": recall_memories
        }

# def load_memories(state: AgentState, config: RunnableConfig) -> AgentState:
#     """Load relevant memories for the conversation."""
#     convo_str = get_buffer_string(state["messages"])
#     convo_str = tokenizer.decode(tokenizer.encode(convo_str)[:2048])
#     print("search_recall_memories =", search_recall_memories)
#     print("type =", type(search_recall_memories))

    
#     recall_documents = search_recall_memories.invoke(
#         {"comb_str": convo_str},
#         config=config
#     )

#     if not isinstance(recall_documents, list):
#         raise ValueError("Expected a list from recall_documents, got:", type(recall_documents))

#     recall_memories = [
#         doc.page_content for doc in recall_documents
#         if isinstance(doc, Document)
#     ]

#     return {
#         **state,
#         "recall_memories": recall_memories
#     }



def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def retry_last_tool(state: AgentState) -> AgentState:
    last_tool = state["last_tool"]
    original_args = state["last_tool_args"]
    rewritten_query = state.get("rewritten_query", "")

    new_args = original_args.copy()
    new_args["query"] = rewritten_query

    tool_result = tools_by_name[last_tool].invoke(new_args)

    tool_msg = ToolMessage(
        content=json.dumps(tool_result),
        name=last_tool,
        tool_call_id="",  
    )

    return {
        **state,
        "messages": state["messages"] + [tool_msg],
        "last_tool": last_tool,
        "last_tool_args": new_args, 
        "user_satisfied": False,
        "rewritten_query": rewritten_query
    }

def check_satisfaction(state: AgentState):
    if state.feedback and state.feedback.lower() in ["yes", "y"]:
        state.satisfied = True
        return "end"
    else:
        return "awaiting_user_rewrite"


def get_user_feedback(state: AgentState):
    return {"__type__": "pause", "name": "awaiting_user_feedback"}






