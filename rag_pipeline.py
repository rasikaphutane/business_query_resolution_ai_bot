# rag_pipeline.py
import logging
from typing import Tuple
from joblib import load

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate

# ========== Setup Logging ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

from pathlib import Path
import json

# === Feedback, Caching, and Learning State ===
CACHE = {}
FEEDBACK_FILE = Path("feedback_log.json")
FEEDBACK_FILE.touch(exist_ok=True)

def load_feedback():
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_feedback(query: str, answer: str, topic: str):
    data = load_feedback()
    data.append({"query": query, "answer": answer, "topic": topic})
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_cache(query: str):
    return CACHE.get(query)

def update_cache(query: str, result: str):
    CACHE[query] = result


# ========== Load Global Components ==========
try:
    logger.info("📦 Loading classifier and encoder...")
    clf = load("topic_classifier.joblib")
    label_encoder = load("label_encoder.joblib")

    logger.info("📦 Loading embedding model (MiniLM)...")
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    logger.info("📦 Initializing ChromaDB...")
    vectordb = Chroma(
        persist_directory="chroma_index",
        embedding_function=embedder
    )

    logger.info("⚙️ Initializing LLM (Mistral via Ollama)...")
    llm = Ollama(base_url="http://host.docker.internal:11434", model="mistral")
    #llm = Ollama(model="mistral", base_url="http://localhost:11434") #local machine

    # Warm up LLM
    logger.info("🔥 Warming up LLM...")
    _ = llm.invoke("Hello")  # Basic dummy call to warm up model
except Exception as e:
    logger.error(f"❌ Initialization failed: {e}")
    raise

# ========== Topic Classifier ==========
def classify_topic(query: str) -> str:
    try:
        vector = embedder.embed_query(query)
        prediction = clf.predict([vector])[0]
        topic = label_encoder.inverse_transform([prediction])[0]
        logger.info(f"📌 Predicted Topic: {topic}")
        return topic
    except Exception as e:
        logger.error(f"❌ Topic classification failed: {e}")
        raise

# ========== Get Topic-Aware RAG Chain ==========
def get_topic_filtered_rag_chain(query: str) -> Tuple[RetrievalQA, str]:
    topic = classify_topic(query)
    try:
        retriever = vectordb.as_retriever(
            search_kwargs={"k": 2, "filter": {"topic": topic}}
        )

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=f"""You are a helpful assistant answering support-related business queries.
Use only the context provided to answer the user's query. If the context is insufficient or unrelated, say:

"I'm sorry, I don't have enough information to answer that based on current data."

Question: {{question}}
Context: {{context}}

Answer:"""

        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True
        )
        return qa_chain, topic
    except Exception as e:
        logger.error(f"❌ Failed to build RAG chain: {e}")
        raise

# ========== CLI for Testing ==========
def main():
    try:
        query = input("❓ Ask your question: ").strip()

        # Handle greeting early
        if query.lower() in {"hello", "hi", "hey"}:
            print("\n🤖 Hello! How can I help you today?\n")
            return

        chain, topic = get_topic_filtered_rag_chain(query)
        output = chain.invoke({"query": query})

        print(f"\n🎯 Final Answer (Topic: {topic}):\n{output['result']}\n")
        print("📚 Source Chunks:")
        for doc in output["source_documents"]:
            print(f"- {doc.page_content[:200]}...\n")

    except Exception as e:
        logger.error(f"❌ Query failed: {e}")

if __name__ == "__main__":
    main()
