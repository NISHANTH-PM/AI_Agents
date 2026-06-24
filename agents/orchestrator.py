import os
from google import genai
from agents.retrieval import answer_query
from agents.insights import generate_insights
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def classify_query(query):
    response = client_ai.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"""Classify this query into exactly one word: either 'retrieval' or 'insights'

Rules:
- 'retrieval' = specific question needing a direct answer
- 'insights' = broad topic needing analysis, patterns, trends

Query: {query}

Reply with only one word:"""
    )
    return response.text.strip().lower()

def orchestrate(query):
    intent = classify_query(query)
    print(f"Intent detected: {intent}")
    
    if "insights" in intent:
        return generate_insights(query)
    else:
        return answer_query(query)