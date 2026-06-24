import os
from qdrant_client import QdrantClient
from google import genai
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "community_data"

def get_embedding(text):
    result = client_ai.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

def retrieve(query, top_k=5):
    query_vector = get_embedding(query)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    return [r.payload["text"] for r in results.points]

def answer_query(query):
    contexts = retrieve(query)
    context_text = "\n".join(contexts)
    
    response = client_ai.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"""You are a community intelligence assistant.
Answer the question using only the context below.

Context:
{context_text}

Question: {query}
Answer:"""
    )
    return response.text