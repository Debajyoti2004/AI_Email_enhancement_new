from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_core.runnables import RunnableConfig
import uuid
import json
import sys
import os
from typing import Optional, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Retriever import retriever
from CreateMemory import store, get_user_id
from Refinement_agent import compile_refinement_agent
from ContextReplyAgent import compile_reply_agent
from Composing_mail import compile_generate_agent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from LLM_fallback import llm_fallback_chain
load_dotenv()

composing_agent = compile_generate_agent()
reply_agent = compile_reply_agent()
refinement_agent = compile_refinement_agent()

def _save_recall_memory(memory: str | dict | list, config: RunnableConfig) -> None:
    print("helper call for _save_recall_memory")
    user_id = get_user_id(config)
    document = Document(
        page_content=memory, id=str(uuid.uuid4()), metadata={"user_id": user_id}
    )
    store.add_documents([document])
    print(f"Memory saved for user {user_id}")


@tool(description="Search for up to 3 relevant memory entries based on a combined query string.")
def search_recall_memories(comb_str: str, config: RunnableConfig) -> List[str]:
    print("tool call for search_recall_memories")
    user_id = get_user_id(config)

    def _filter_function(doc: Document) -> bool:
        return doc.metadata.get("user_id") == user_id

    documents = store.similarity_search(
        comb_str, k=3, filter=_filter_function
    )
    return "\n---\n".join([doc.page_content for doc in documents])

@tool(description="Retrieve contextually relevant GoFlow documents using the email subject and query.")
def Retrieve_data_on_goflow(query: str, email_sub: Optional[str] = None, config: Optional[RunnableConfig] = None) -> List[str]:
    print("tool call for Retrieve_data")
    combined_str = f"""
     Email subject:{email_sub}
     Query:{query}"""

    documents = retriever.get_relevant_documents(combined_str)

    if not documents:
        return ["No relevant content found in memory."]

    print("\n[Retrieved Documents]")
    for doc in documents:
        print("-", doc.page_content)

    return "\n---\n".join([doc.page_content for doc in documents])


@tool(description="Refine a user-composed email using an agent and save the result in memory.")
def refinement_tool(email_input: dict[str, str], query: str, config: RunnableConfig) -> str:
    print("tool call for refinement_tool")
    response = refinement_agent.invoke({
        "email": email_input,
        "query": query
    })

    refined_email = response["refined_email"]
    refined_email_str = json.dumps(refined_email)

    _save_recall_memory(memory=refined_email_str, config=config)
    return refined_email_str

@tool(description="Generate a reply to an email using a reply agent and store the result in memory.")
def reply_agent_tool(email_input: dict[str, str], query: str, previous_responses: str,retrieved_company_data:str, config: RunnableConfig) -> str:
    print("tool call for reply_agent_tool")

    response = reply_agent.invoke({
        "previous_response": previous_responses,
        "email": email_input,
        "query": query,
        "context": retrieved_company_data
    })

    result = response["generate_email"]
    result_str = json.dumps(result)
    email_input_str = json.dumps(email_input)

    combined_str = email_input_str + result_str + previous_responses
    _save_recall_memory(memory=combined_str, config=config)

    return result

@tool(description="Compose a new email based on the user's input and query, using company data as context.")
def composing_email_tool(email_details: dict[str, str], query: str,retrieved_company_data:str, config: RunnableConfig) -> str:
    print("tool call for composing_email_tool")

    response = composing_agent.invoke({
        "email": email_details,
        "query": query,
        "context": retrieved_company_data
    })

    result = response["generate_email"]
    result_str = json.dumps(result)
    _save_recall_memory(memory=result_str, config=config)

    return result_str

@tool(description="Check whether previous responses answer the current query using fallback LLM and contextual data.")
def previous_response_checker_tool(query: str,previous_responses:str,required_company_data:str,config: RunnableConfig) -> str:
    print("tool call for previous_response_checker_tool")

    if not previous_responses:
        return "No matching previous responses found."

    combined_data = previous_responses + required_company_data

    response = llm_fallback_chain.invoke(
        {
            "query": query,
            "previous_response": combined_data
        }
    )
    _save_recall_memory(memory=response, config=config)
    return f"Based on your previous queries and responses, here's what I found:\n{response}"
