import os
from google import genai
from agents.retrieval import retrieve
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_insights(topic, collection_name="members"):
    contexts = retrieve(topic, collection_name=collection_name, top_k=10)
    context_text = "\n".join(contexts)

    response = generate_content(f"""You are a community analytics expert.
Analyze the following community data and generate insights, patterns and trends.

Data:
{context_text}

Topic: {topic}

Provide:
1. Key patterns you notice
2. Top performers
3. Trends
4. Recommendations for the community
""")
    
    return response

GENERATION_MODELS = [
    "models/gemini-3.5-flash",
    "models/gemini-2.5-flash"
]

current_gen_model_index = 0

def generate_content(prompt):
    global current_gen_model_index
    
    while current_gen_model_index < len(GENERATION_MODELS):
        model = GENERATION_MODELS[current_gen_model_index]
        try:
            response= client_ai.models.generate_content(
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