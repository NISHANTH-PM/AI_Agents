import os
import json
import time
import threading
import datetime
from agents.insights import generate_insights
from dotenv import load_dotenv
import logging

os.makedirs('logs', exist_ok=True)
os.makedirs('cache', exist_ok=True)

logging.basicConfig(
    filename='logs/scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

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
    print(f"Looking for cache at: {os.path.abspath(CACHE_FILE)}")
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    print("Cache file not found!")
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def refresh_insights():
    cache = load_cache()  # load existing first
    for domain in DOMAINS:
        try:
            topic = DOMAIN_TOPICS[domain]
            insight = generate_insights(topic, collection_name=domain)
            cache[domain] = {
                "insight": insight,
                "generated_at": str(datetime.datetime.now())
            }
        except Exception as e:
            logging.error(f"Failed for {domain}: {e}")
            # keeps old cache for this domain
    save_cache(cache)

def get_cached_insight(domain):
    cache = load_cache()
    print(f"Cache keys: {list(cache.keys())}")
    if domain in cache:
        return cache[domain]["insight"]
    return None

def start_scheduler():
    def run():
        time.sleep(3600)  # wait 1 hour before first refresh
        while True:
            refresh_insights()
            time.sleep(INTERVAL_HOURS * 3600)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    