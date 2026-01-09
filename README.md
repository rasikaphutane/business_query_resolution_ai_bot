# 🤖 Business Query Resolution AI Bot

A production-ready, full-stack **AI assistant** that answers business questions using a **Retrieval-Augmented Generation (RAG)** system.

---

## 📌 Project Overview

This system helps users get accurate and context-aware answers to business-related queries by combining:

- Document retrieval  
- Large language models  
- Secure authentication  
- Scalable deployment  

---

## ✨ Key Features

1. Uses **FastAPI + LangChain + Mistral (via Ollama)** for intelligent query handling  
2. Classifies each query to understand user intent  
3. Retrieves relevant information from **CSV documents stored in ChromaDB**  
4. Combines retrieved context with the LLM to generate **accurate answers**  
5. Secures access using **JWT authentication**  
6. Stores **persistent chat history** for every user  
7. Provides a clean and responsive **TailwindCSS frontend**  
8. Fully **Dockerized** for easy deployment  

---

## 🛠 Tech Stack

### Backend
1. FastAPI  
2. LangChain  
3. Ollama (Mistral)  
4. ChromaDB  

### Frontend
1. HTML  
2. TailwindCSS  
3. JavaScript  

### Security & Deployment
1. JWT Authentication  
2. Docker  
3. Docker Compose  

---

## 🔄 How It Works

1. User logs in securely  
2. User submits a business query  
3. System classifies the query  
4. Relevant documents are retrieved from ChromaDB  
5. Context is sent to the LLM  
6. AI generates a clear and grounded response  
7. Chat history is saved for future reference  

---

## 🚀 Use Cases

1. Internal company knowledge assistant  
2. Customer support automation  
3. HR policy and employee queries  
4. Finance and operations support  
5. Document-based Q&A systems  

---

## 📈 Future Enhancements

1. Role-based access control  
2. Support for multiple LLMs  
3. Document upload dashboard  
4. Analytics and usage tracking  
5. Voice-based query support  

