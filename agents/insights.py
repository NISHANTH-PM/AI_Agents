import os
from google import genai
from agents.retrieval import retrieve
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_insights(topic):
    contexts = retrieve(topic, top_k=10)
    context_text = "\n".join(contexts)

    response = client_ai.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"""You are a community analytics expert.
Analyze the following community data and generate insights, patterns and trends.

Data:
{context_text}

Topic: {topic}

Provide:
1. Key patterns you notice
2. Top performers
3. Trends
4. Recommendations for the community
"""
    )
    return response.text