import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agents.orchestrator import orchestrate
from scheduler import get_cached_insight, refresh_insights
from dotenv import load_dotenv
import pandas as pd
from tools.mcp_tools import call_tool, list_tools

load_dotenv()

app = FastAPI()

DOMAIN_TOPICS = {
    "members": "member performance, skills, attendance and roles",
    "events": "event participation, satisfaction and attendance trends",
    "communications": "communication effectiveness, open rates and engagement",
    "finance": "budget allocation, spending patterns and financial health",
    "projects": "project completion, team performance and impact"
}

@app.get("/mcp/tools")
def get_tools():
    return list_tools()

@app.get("/mcp/call/{tool_name}")
def execute_tool(tool_name: str):
    return call_tool(tool_name)

@app.get("/insights/{domain}")
def get_insights(domain: str):
    from agents.insights import generate_insights
    from scheduler import get_cached_insight
    
    # Try cache first
    insight = get_cached_insight(domain)
    
    # If cache is bad/empty, generate live
    if not insight or len(insight) < 100:
        insight = generate_insights(
            DOMAIN_TOPICS.get(domain, domain),
            collection_name=domain
        )
    
    return {"domain": domain, "insight": insight}

@app.get("/anomalies")
def get_anomalies():
    alerts = []
    try:
        # Events: low attendance
        df = pd.read_csv("data/events.csv")
        low = df[df['attendance_rate'] < 0.5]
        for _, row in low.iterrows():
            alerts.append({
                "type": "warning",
                "domain": "events",
                "message": f"Low attendance: {row['event_name']} ({round(row['attendance_rate']*100)}%)"
            })

        # Finance: overspent
        df = pd.read_csv("data/finance.csv")
        if 'budget_allocated' in df.columns and 'budget_spent' in df.columns:
            over = df[df['budget_spent'] > df['budget_allocated']]
            for _, row in over.iterrows():
                alerts.append({
                    "type": "danger",
                    "domain": "finance",
                    "message": f"Budget overrun: {row.get('category', 'Unknown')} (${row['budget_spent']})"
                })

        # Members: low attendance
        df = pd.read_csv("data/members.csv")
        low = df[df['attendance_pct'] < 50]
        for _, row in low.iterrows():
            alerts.append({
                "type": "warning",
                "domain": "members",
                "message": f"Low attendance: {row['name']} ({row['attendance_pct']}%)"
            })

        # Projects: overdue
        df = pd.read_csv("data/projects.csv")
        overdue = df[(df['completion_pct'] < 50) & (df['status'] == 'Active')]
        for _, row in overdue.iterrows():
            alerts.append({
                "type": "danger",
                "domain": "projects",
                "message": f"At risk: {row['project_name']} ({row['completion_pct']}% complete)"
            })

    except Exception as e:
        alerts.append({"type": "danger", "domain": "system", "message": str(e)})

    return {"alerts": alerts[:10]}  # cap at 10     

@app.get("/stats/{domain}")
def get_stats(domain: str):
    try:
        df = pd.read_csv(f"data/{domain}.csv")
        if domain == "members":
            counts = df['role'].value_counts().to_dict()
            return {"labels": list(counts.keys()), "data": list(counts.values())}
        elif domain == "events":
            counts = df['event_type'].value_counts().to_dict()
            return {"labels": list(counts.keys()), "data": list(counts.values())}
        elif domain == "communications":
            counts = df['channel'].value_counts().to_dict()
            return {"labels": list(counts.keys()), "data": list(counts.values())}
        elif domain == "finance":
            counts = df['category'].value_counts().to_dict()
            return {"labels": list(counts.keys()), "data": list(counts.values())}
        elif domain == "projects":
            counts = df['status'].value_counts().to_dict()
            return {"labels": list(counts.keys()), "data": list(counts.values())}
    except Exception as e:
        return {"labels": [], "data": [], "error": str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "Community Intelligence Agent Running"}

@app.get("/dashboard")
def dashboard():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory="."), name="static")

@app.post("/ask")
def ask(query: Query):
    response = orchestrate(query.question)
    return {"answer": response}

@app.get("/insights/{domain}")
def get_insights(domain: str):
    insight = get_cached_insight(domain)
    if insight:
        return {"domain": domain, "insight": insight}
    return {"domain": domain, "insight": "No insights cached yet."}

@app.get("/insights")
def get_all_insights():
    domains = ["members", "events", "communications", "finance", "projects"]
    cache = {}
    for domain in domains:
        insight = get_cached_insight(domain)
        cache[domain] = insight or "No insights cached yet."
    return cache

@app.post("/refresh")
def refresh():
    refresh_insights()
    return {"status": "Insights refreshed"}