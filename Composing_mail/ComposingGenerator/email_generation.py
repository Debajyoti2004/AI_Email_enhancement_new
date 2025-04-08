from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os
load_dotenv()


# Prompt Template
template = """
You are an expert **{email_type} Email Assistant**. Your task is to generate a well-structured and professional email body based on the provided details.

### **Email Type:** {email_type}

### **Email Details (Extract Required Fields)**
{email}

### **User Query**
{query}

### **Contextual Information:**
{context}
---

## **Task:**
- Compose a **natural and professional email body** relevant to the subject and query.
- Ensure **clarity, conciseness, and accuracy**.
- Adapt tone and content **based on the specified email type**.
- **Extract key details (From, To, Subject) from the given email details.**

---

## **Rules:**
    - Maintain a professional tone suitable for the given email type.
    - Avoid predefined templates; generate a fresh response based on context.
    - Ensure the response is well-structured and relevant.

Respond strictly in the following JSON format:
{{
  "from": "<sender email>",
  "to": "<receiver email>",
  "subject": "<email subject>",
  "body": "<well-structured email content>"
}}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["email_type", "email", "query", "context"]
)

structured_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=os.getenv("COMPOSER_GOOGLE_API_KEY")
)

# Full email generation chain
email_generation_chain = (
    prompt
    | structured_llm
    | JsonOutputParser()
)
