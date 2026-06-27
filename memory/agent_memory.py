import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google import genai
from dotenv import load_dotenv
import uuid
import datetime

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=30
)

MEMORY_COLLECTION = "agent_memory"

def create_memory_collection():
    client.recreate_collection(
        collection_name=MEMORY_COLLECTION,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
    )

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
            return result.embeddings[0].values
        except Exception as e:
            if "429" in str(e):
                current_model_index += 1
            else:
                raise e
    return None

def save_to_memory(query, response):
    text = f"User asked: {query} | Agent answered: {response}"
    embedding = get_embedding(text)
    client.upsert(
        collection_name=MEMORY_COLLECTION,
        points=[PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "query": query,
                "response": response,
                "timestamp": str(datetime.datetime.now())
            }
        )]
    )

def recall_memory(query, top_k=3):
    embedding = get_embedding(query)
    results = client.query_points(
        collection_name=MEMORY_COLLECTION,
        query=embedding,
        limit=top_k
    )
    if not results.points:
        return "No relevant memory found."
    
    memory_text = ""
    for r in results.points:
        memory_text += f"Previously asked: {r.payload['query']}\n"
        memory_text += f"Answer was: {r.payload['response']}\n\n"
    return memory_text