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

load_dotenv()

app = FastAPI()

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