from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

prompt = PromptTemplate(
    template="""You are an expert at solving user query based on previous response given by agents.
    The user query is: {query}.
    This is the Previous Response given by agents: {previous_response}
    Based on the above information, please provide a detailed and accurate response.

    llm response:
    """,
    input_variables=["query", "previous_response"],
)
llm = ChatGoogleGenerativeAI(
    model="google-2.0-flash",
    temperature=0,
    api_key=os.getenv("GOOGLE_API_KEY_1"),
)

llm_fallback_chain = (prompt
                      | llm
                      | StrOutputParser()
)