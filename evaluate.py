import pandas as pd
from joblib import load
from sklearn.metrics import classification_report, accuracy_score
from tqdm import tqdm
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate

# Load components
clf = load("topic_classifier.joblib")
label_encoder = load("label_encoder.joblib")
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # ✅ works with embed_query()
  # Pretrained HuggingFaceEmbeddings dumped earlier

# Load evaluation dataset
df = pd.read_csv("test_queries.csv")  # Must have: Document, Topic_group

# Load Chroma vector store
vectordb = Chroma(
    persist_directory="chroma_index",
    embedding_function=embedder
)

# LLM for answering
llm = Ollama(model="mistral")

# Evaluation
true_topics = []
predicted_topics = []
answers = []

print("🧪 Evaluating model...")
for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating"):
    query = row["Document"]
    true_topic = row["Topic_group"]
    true_topics.append(true_topic)

    # Predict topic
    query_emb = embedder.embed_query(query)
    predicted_label_id = clf.predict([query_emb])[0]
    predicted_topic = label_encoder.inverse_transform([predicted_label_id])[0]
    predicted_topics.append(predicted_topic)

    # Use topic-filtered retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": 5, "filter": {"topic": predicted_topic}})

    # RAG prompt
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=f"""You are an expert assistant for IT support.
Only use the context related to topic: {predicted_topic} to answer the user's question.
If there's insufficient context, say you don't have enough information.

Question: {{question}}
Context: {{context}}
Answer:"""
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=False
    )

    response = qa_chain.invoke({"query": query})
    answers.append(response["result"])

# Save predictions
df["Predicted_Topic"] = predicted_topics
df["Answer"] = answers
df.to_csv("evaluation_results.csv", index=False)

# Print metrics
print("\n🔍 Topic Classification Report:")
print(classification_report(true_topics, predicted_topics))
print("✅ Accuracy Score:", accuracy_score(true_topics, predicted_topics))
