import os
from qdrant_client import QdrantClient
from google import genai
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=30
)

EMBEDDING_MODELS = [
    "models/gemini-embedding-001",
    "models/gemini-embedding-2-preview"
]

current_model_index = 0

GENERATION_MODELS = [
    "models/gemini-3.5-flash",
    "models/gemini-3.1-flash-lite",
    "models/gemini-3-flash-preview",
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-lite"
]

current_gen_model_index = 0

def generate_content(prompt):
    global current_gen_model_index
    
    while current_gen_model_index < len(GENERATION_MODELS):
        model = GENERATION_MODELS[current_gen_model_index]
        try:
            response = client_ai.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                current_gen_model_index += 1
            else:
                raise e
    
    return "All models exhausted. Try again later."

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

def retrieve(query, collection_name="members", top_k=5):
    query_vector = get_embedding(query)
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    )
    return [r.payload["text"] for r in results.points]

def answer_query(query, collection_name="members"):
    contexts = retrieve(query, collection_name=collection_name)
    context_text = "\n".join(contexts)

    response = generate_content(f"""You are a community intelligence assistant.
Answer the question using only the context below.

Context:
{context_text}

Question: {query}
Answer:"""
    )
    return response