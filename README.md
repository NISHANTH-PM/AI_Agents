# Community Intelligence Agent

Deployed Link: https://ai-agents-6sus.onrender.com/dashboard

An AI-powered multi-agent system that transforms community and organizational data into actionable insights using Google ADK, Gemini, and Qdrant.

## Problem Statement
**PS2 - Club & Community Intelligence Agent**  
Built for the Google x Hidev Hackathon 2026

## What it does
- **Answers natural language questions** about members, events, finance, projects, and communications
- **Generates AI insights** with pattern recognition and trend analysis
- **Proactive anomaly detection** — flags at-risk projects, low attendance, budget overruns
- **Auto-suggests follow-up questions** after every response
- **Voice input** support for hands-free querying
- **Pre-cached insights** refreshed every 6 hours automatically

## Architecture
User Query
→ Orchestrator (classifies domain + intent)## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | Google ADK |
| LLM | Gemini 3.5 Flash + Gemini 2.5 Flash (fallback) |
| Embeddings | Gemini Embedding 001 + Embedding 2 Preview (fallback) |
| Vector Database | Qdrant Cloud (GCP Sydney) |
| Backend API | FastAPI |
| Frontend | HTML + Tailwind CSS + Chart.js |
| Memory | Qdrant (agent_memory collection) |
| Scheduler | Python Threading (6-hour cache refresh) |

## RAG Architecture
This project implements **Adaptive Branched RAG**:
- Query classified by **domain** (members/events/finance/projects/communications)
- Query classified by **intent** (retrieval vs insights)
- Routed to the correct Qdrant collection
- Context retrieved and passed to Gemini for generation

## Project Structure
→ Retrieval Agent (specific questions) → Qdrant → Gemini → Answer
→ Insights Agent (broad analysis) → Qdrant → Gemini → Analysis
→ Memory Agent (saves Q&A for future recall)
→ Scheduler (runs independently, pre-caches insights every 6 hours)
├── agents/
│   ├── orchestrator.py    # Domain + intent classification and routing
│   ├── ingestion.py       # Data ingestion with embedding + auto model fallback
│   ├── retrieval.py       # Semantic search + RAG query answering
│   └── insights.py        # Pattern recognition and trend analysis
├── memory/
│   └── agent_memory.py    # Long-term conversation memory
├── scheduler.py           # Background 6-hour insights cache refresh
├── api.py                 # FastAPI backend
├── main.py                # CLI entry point
├── index.html             # Dashboard frontend
└── .env                   # API keys (not committed)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/community-intelligence-agent
cd community-intelligence-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Add your API keys to .env
```

### 5. Ingest data
```bash
python -c "from agents.ingestion import create_all_collections, ingest_all; create_all_collections(); ingest_all()"
```

### 6. Run the server
```bash
uvicorn api:app --reload
```

### 7. Open dashboard
http://localhost:8000/dashboard

## Environment Variables
GOOGLE_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key


## Key Features
- **Auto model fallback** — switches embedding/generation models automatically on rate limits
- **Branched RAG** — 5 separate vector collections for precise domain routing
- **6-hour scheduler** — pre-generates insights so dashboard loads instantly
- **Long-term memory** — remembers past queries and answers across sessions
- **Anomaly detection** — proactively flags issues without being asked






