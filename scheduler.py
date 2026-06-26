import os
import json
import time
import threading
import datetime
from agents.insights import generate_insights
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "cache/insights_cache.json"
DOMAINS = ["members", "events", "communications", "finance", "projects"]
INTERVAL_HOURS = 6

DOMAIN_TOPICS = {
    "members": "member performance, skills, attendance and roles",
    "events": "event participation, satisfaction and attendance trends",
    "communications": "communication effectiveness, open rates and engagement",
    "finance": "budget allocation, spending patterns and financial health",
    "projects": "project completion, team performance and impact"
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def refresh_insights():
    print(f"[{datetime.datetime.now()}] Refreshing insights cache...")
    cache = load_cache()
    
    for domain in DOMAINS:
        try:
            print(f"Generating insights for: {domain}")
            topic = DOMAIN_TOPICS[domain]
            insight = generate_insights(topic, collection_name=domain)
            cache[domain] = {
                "insight": insight,
                "generated_at": str(datetime.datetime.now())
            }
            time.sleep(2)  # avoid rate limiting between domains
        except Exception as e:
            print(f"Failed for {domain}: {e}")
    
    save_cache(cache)
    print("Cache updated.")

def get_cached_insight(domain):
    cache = load_cache()
    if domain in cache:
        return cache[domain]["insight"]
    return None

def start_scheduler():
    def run():
        while True:
            refresh_insights()
            print(f"Next refresh in {INTERVAL_HOURS} hours.")
            time.sleep(INTERVAL_HOURS * 3600)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("Scheduler started.")