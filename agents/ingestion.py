import os
import pandas as pd
import pypdf
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google import genai
from dotenv import load_dotenv
import uuid

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTIONS = {
    "members": 3072,
    "events": 3072,
    "communications": 3072,
    "finance": 3072,
    "projects": 3072
}

# Map CSV files to collections
CSV_COLLECTION_MAP = {
    "members.csv": "members",
    "events.csv": "events",
    "communications.csv": "communications",
    "finance.csv": "finance",
    "projects.csv": "projects"
}

def create_all_collections():
    for name, size in COLLECTIONS.items():
        client.recreate_collection(
            collection_name=name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE)
        )
        print(f"Collection created: {name}")

import time

EMBEDDING_MODELS = [
    "models/gemini-embedding-001",
    "models/gemini-embedding-2-preview"
]

current_model_index = 0

def get_embedding(text):
    global current_model_index
    
    while current_model_index < len(EMBEDDING_MODELS):
        model = EMBEDDING_MODELS[current_model_index]
        try:
            result = client_ai.models.embed_content(
                model=model,
                contents=text
            )
            time.sleep(0.7)
            return result.embeddings[0].values
        except Exception as e:
            if "429" in str(e):
                print(f"{model} rate limited. Switching permanently to next model...")
                current_model_index += 1
            elif "503" in str(e):
                print(f"Server unavailable. Waiting 30s...")
                time.sleep(30)
            else:
                raise e
    
    print("All models exhausted.")
    return None

def ingest_csv(filepath, collection_name=None):
    filename = os.path.basename(filepath)
    if collection_name is None:
        collection_name = CSV_COLLECTION_MAP.get(filename)
    if collection_name is None:
        print(f"No collection mapped for {filename}, skipping.")
        return

    df = pd.read_csv(filepath)
    points = []
    for _, row in df.iterrows():
        text = " ".join([str(v) for v in row.values])
        embedding = get_embedding(text)
        if embedding is None:
            print(f"Skipping row due to failed embedding: {text[:50]}")
            continue
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text, "source": filename, **row.to_dict()}
        ))
    client.upsert(collection_name=collection_name, points=points)
    print(f"Ingested {len(points)} rows into '{collection_name}' from {filename}")
    
def ingest_all(data_dir="data"):
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv") and filename in CSV_COLLECTION_MAP:
            ingest_csv(os.path.join(data_dir, filename))