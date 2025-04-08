from langchain_cohere import ChatCohere
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

class EmailClassifier(BaseModel):
    email_tone: Literal[
        "Friendly", "Professional", "Assertive", "Empathetic", "Persuasive", "Neutral"
    ] = Field(description="The overall tone of the email.")


prompt = PromptTemplate(
    template="""
You are an expert email classification assistant. Your job is to classify the tone of the email.

Email Tone (choose one):
- Friendly: Warm, kind, and inviting.
- Professional: Polished and respectful business tone.
- Assertive: Confident, direct, and firm.
- Empathetic: Understanding and emotionally considerate.
- Persuasive: Trying to convince or influence.
- Neutral: Objective and emotionless.

Email:
{email_input}

Return the category and tone as structured JSON output.
""",
    input_variables=["email_input"]
)

  
llm = ChatCohere(
  cohere_api_key=os.getenv("CLASSIFIER_COHERE_API_KEY"),
  temperature=0
).bind_tools(
  tools=[EmailClassifier]
)

email_classifier_chain = (
  prompt
  | llm
)



