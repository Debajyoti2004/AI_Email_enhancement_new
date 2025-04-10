
https://github.com/user-attachments/assets/e044f8de-59cc-4c61-90fc-6dd83c1a39e9
# 📬 Atom Email Assistant — RAG-Powered Smart Email Helper

The **Atom Email Assistant** is an intelligent tool designed to enhance email composition and replies using **RAG (Retrieval-Augmented Generation)**. It remembers previous interactions, retrieves relevant context, and provides professional and context-aware responses just like ChatGPT.

![Screenshot](https://github.com/user-attachments/assets/058ce723-6c04-4482-ad8a-0ae8436a0d59)

---

## 🚀 Features

- ✉️ Smart email drafting & replying  
- 🧠 Memory-powered multi-turn conversation  
- 📚 Retrieval-Augmented Generation using custom knowledge  
- 💬 ChatGPT-style interface with chat history  
- 🧹 Clear chat history on demand  

---

## 🛠️ Tech Stack

- **Flask** – lightweight backend  
- **LangChain** – for building RAG pipeline  
- **FAISS / Chroma** – vector store for document retrieval  
- **Gemini 2.0 Flash** and **Cohere** – LLM for generation  
- **HTML + JS + CSS** – responsive frontend  

---

## 🎥 Demo

> 📽️ Watch how Atom Email Assistant helps generate intelligent email replies in seconds:

<video width="100%" controls>
  <source src="Uploading atom email.mp4…">
  Your browser does not support the video tag.
</video>

---

## 🧠 How It Works

1. **User asks a query** (e.g., _"Reply to this client about delay politely."_)  
2. The **RAG pipeline**:  
   - Searches through email history / past documents using FAISS  
   - Sends query + retrieved context to the LLM  
3. The **LLM generates a response**, which is displayed to the user  
4. All interactions are stored in session for context retention  

---

## ⚙️ How to Run Locally

```bash
git clone https://github.com/Debajyoti2004/AI_Email_enhancement_new.git
cd app
pip install -r requirements.txt
python app.py
