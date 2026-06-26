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
    response = generate_content(
        f"""Classify this query into exactly one of these domains:
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
    return response.strip().lower()

def classify_intent(query):
    response = generate_content(f"""Classify this query into exactly one word: either 'retrieval' or 'insights'

Rules:
- retrieval = specific question needing a direct answer
- insights = broad topic needing analysis, patterns, trends

Query: {query}

Reply with only one word:""")
    
    return response.strip().lower()

def orchestrate(query):
    # Recall memory
    memory = recall_memory(query)
    

    # Classify domain and intent
    domain = classify_domain(query)
    intent = classify_intent(query)
    
    # Validate domain
    if domain not in DOMAINS:
        domain = "members"  # default fallback
    
    

    if "insights" in intent:
        response = generate_insights(query, collection_name=domain)
    else:
        response = answer_query(query, collection_name=domain)

    save_to_memory(query, response)
    return response

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