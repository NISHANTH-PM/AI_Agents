import os
from google import genai
from agents.retrieval import answer_query
from agents.insights import generate_insights
from memory.agent_memory import save_to_memory, recall_memory
from dotenv import load_dotenv

load_dotenv()

client_ai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

DOMAINS = ["members", "events", "communications", "finance", "projects"]

def classify_domain(query):
    response = client_ai.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"""Classify this query into exactly one of these domains:
members, events, communications, finance, projects

Rules:
- members = questions about people, roles, skills, attendance, GPA, placement
- events = questions about competitions, workshops, meetups, attendance
- communications = questions about announcements, emails, messages, open rates
- finance = questions about budget, expenses, transactions, spending
- projects = questions about ongoing work, teams, completion, tech stack

Query: {query}

Reply with only one word from the list above:"""
    )
    return response.text.strip().lower()

def classify_intent(query):
    response = client_ai.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=f"""Classify this query into exactly one word: either 'retrieval' or 'insights'

Rules:
- retrieval = specific question needing a direct answer
- insights = broad topic needing analysis, patterns, trends

Query: {query}

Reply with only one word:"""
    )
    return response.text.strip().lower()

def orchestrate(query):
    # Recall memory
    memory = recall_memory(query)
    print(f"Memory recalled: {memory}")

    # Classify domain and intent
    domain = classify_domain(query)
    intent = classify_intent(query)
    
    # Validate domain
    if domain not in DOMAINS:
        domain = "members"  # default fallback
    
    print(f"Domain: {domain} | Intent: {intent}")

    if "insights" in intent:
        response = generate_insights(query, collection_name=domain)
    else:
        response = answer_query(query, collection_name=domain)

    save_to_memory(query, response)
    return response