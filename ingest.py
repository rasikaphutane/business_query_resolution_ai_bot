import pandas as pd
import time
from tqdm import tqdm
from collections import defaultdict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def ingest_csv(path="trimmed_tickets.csv", persist_dir="chroma_index", model_name="all-MiniLM-L6-v2"):
    start_time = time.time()
    print("🔄 Starting ingestion...\n")

    # Step 1: Load CSV
    t0 = time.time()
    df = pd.read_csv(path)
    print(f"📄 Loaded CSV with {len(df)} rows in {time.time() - t0:.2f}s")

    # Step 2: Convert to LangChain Documents
    documents = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="📄 Creating documents", unit="row"):
        content = str(row['Document']).strip()
        meta = {"topic": row['Topic_group']}
        documents.append(Document(page_content=content, metadata=meta))

    # Step 3: Split into chunks
    t1 = time.time()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks in {time.time() - t1:.2f}s")

    # Step 4: Load HuggingFace MiniLM Embedding Model
    t2 = time.time()
    print(f"🧠 Embedding + Creating Chroma DB using: '{model_name}' ...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Step 5: Create Chroma Vector DB (automatically embeds internally)
    try:
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        vectordb.persist()
        print(f"✅ Chroma DB saved to '{persist_dir}' in {time.time() - t2:.2f}s")
    except Exception as e:
        print(f"❌ Chroma DB creation failed: {e}")
        return

    # Step 6: Print summary
    topic_counts = defaultdict(int)
    for doc in chunks:
        topic_counts[doc.metadata.get("topic", "Unknown")] += 1

    print("\n📊 Chunk distribution per topic:")
    for topic, count in topic_counts.items():
        print(f"  • {topic}: {count} chunks")

    print(f"\n🏁 Ingestion complete in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    ingest_csv()
