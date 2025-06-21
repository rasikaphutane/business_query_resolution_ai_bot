from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import json
import logging
import os
from dotenv import load_dotenv
from rag_pipeline import check_cache, update_cache, save_feedback,get_topic_filtered_rag_chain
from auth import auth_router, get_current_user
from models import User

# Load env vars
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
DB_PATH = os.getenv("DB_PATH")

# App setup
app = FastAPI(title="RAG Support API with History")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.include_router(auth_router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory chat history
chat_history: Dict[str, List[Dict[str, str]]] = {}

# ==== Models ====
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    session_id: str
    predicted_topic: str
    answer: str
    history: List[Dict[str, str]]

# ==== Feedback Logger ====
def log_feedback(username: str, query: str, answer: str, topic: str):
    feedback_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": username,
        "query": query,
        "answer": answer,
        "topic": topic
    }
    with open("feedback_log.jsonl", "a") as f:
        f.write(json.dumps(feedback_entry) + "\n")

# ==== ASK Endpoint ====
@app.post("/ask", response_model=QueryResponse)
async def ask_query(req: QueryRequest, user: User = Depends(get_current_user)):
    logger.info(f"Authenticated user: {user.username}")
    query_clean = req.query.strip().lower()
    session_id = str(uuid4())

    greeting_keywords = ["helo", "hi", "hello", "hey", "greetings", "howdy", "sup", "yo", "what's up", "hi there", "good day"]
    vague_requests = ["help", "support", "assist", "question", "query", "info", "information", "details", "what can you do", "what is your purpose", "what can you help with", "how can you assist", "what are your capabilities", "what do you know", "what topics do you cover"]
    farewell_keywords = ["bye", "goodbye", "see you", "later", "take care", "farewell", "cya", "ttyl", "peace out", "adios","thanks", "thank you", "appreciate it"]

    if query_clean in greeting_keywords:
        return QueryResponse(
            session_id=session_id,
            predicted_topic="Greeting",
            answer="Hello! I'm your support assistant. Ask me anything about your business queries!",
            history=[]
        )

    if query_clean in vague_requests:
        return QueryResponse(
            session_id=session_id,
            predicted_topic="Capabilities",
            answer="I can help you with topic-specific business support queries. Please ask something like:\n- 'How do I request hardware access?'\n- 'What are the onboarding steps for a new employee?'",
            history=[]
        )

    if query_clean in farewell_keywords:
        return QueryResponse(
            session_id=session_id,
            predicted_topic="Farewell",
            answer="You're welcome! Have a great day!",
            history=[]
        )

    # Handle actual RAG pipeline
    try:
        cached_result = check_cache(query_clean)
        if cached_result:
            logger.info(f"⚡ Using cached result for: {query_clean}")
            result = cached_result
            topic = "Cached"
        else:
            chain, topic = get_topic_filtered_rag_chain(query_clean)
            output = chain.invoke({"query": query_clean})
            result = output["result"]
            update_cache(query_clean, result)
            save_feedback(query_clean, result, topic)

        # Update history
        history = chat_history.setdefault(session_id, [])
        history.append({"query": req.query, "answer": result})

        try:
            log_feedback(user.username, req.query, result, topic)
        except Exception as log_err:
            logger.warning(f"⚠️ Feedback logging failed: {log_err}")

        return QueryResponse(
            session_id=session_id,
            predicted_topic=topic,
            answer=result,
            history=history
        )

    except Exception as e:
        logger.error(f"❌ Error in RAG processing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ==== Session History ====
@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {
        "session_id": session_id,
        "history": chat_history.get(session_id, [])
    }

# ==== End Session ====
@app.post("/end_session")
async def end_session(req: QueryRequest, user: User = Depends(get_current_user)):
    session_id = req.session_id
    if not session_id or session_id not in chat_history:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"💾 Finalized chat session: {session_id}")
    return {"message": "Session finalized", "session_id": session_id}
