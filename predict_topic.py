# Modified version of train_classifier.py using MiniLM embeddings instead of TF-IDF
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from joblib import dump
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report

# Load dataset
df = pd.read_csv("all_tickets_processed_improved_v3.csv")
X = df['Document']
y = df['Topic_group']

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Load MiniLM embedder
embedder = SentenceTransformer('all-MiniLM-L6-v2')
X_embedded = embedder.encode(X.tolist(), show_progress_bar=True)

# Train classifier
clf = LogisticRegression(max_iter=1000)
clf.fit(X_embedded, y_encoded)

# Save classifier and label encoder
dump(clf, "topic_classifier.joblib")
dump(label_encoder, "label_encoder.joblib")
dump(embedder, "embedder.joblib")  # Optional: for consistency

print("✅ Classifier and label encoder saved.")

