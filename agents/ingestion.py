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

COLLECTION_NAME = "community_data"

def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
    )
    print("Collection created.")

def get_embedding(text):
    result = client_ai.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

def ingest_csv(filepath):
    df = pd.read_csv(filepath)
    points = []
    for _, row in df.iterrows():
        text = " ".join([str(v) for v in row.values])
        embedding = get_embedding(text)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": text, "source": filepath}
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Ingested {len(points)} rows from {filepath}")

def ingest_pdf(filepath):
    reader = pypdf.PdfReader(filepath)
    points = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            embedding = get_embedding(text)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": text, "source": filepath, "page": i}
            ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Ingested {len(points)} pages from {filepath}")

def ingest_text(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    points = []
    for chunk in chunks:
        if chunk.strip():
            embedding = get_embedding(chunk)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": chunk, "source": filepath}
            ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Ingested {len(points)} chunks from {filepath}")