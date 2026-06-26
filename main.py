import os
from agents.orchestrator import orchestrate
from scheduler import start_scheduler, get_cached_insight
from dotenv import load_dotenv
import threading

load_dotenv()

def main():
     # Start scheduler silently in background
    threading.Thread(target=start_scheduler, daemon=True).start()
    
    print("\n=== Community Intelligence Agent ===\n")

    import time
    time.sleep(0.5)
    threading.Thread(target=start_scheduler, daemon=True).start()
    
    while True:
        print("\nOptions:")
        print("1. Ask a question")
        print("2. View cached insights")
        print("3. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            query = input("Your question: ").strip()
            if query:
                response = orchestrate(query)
                print(f"\nAnswer: {response}")
        
        elif choice == "2":
            domain = input("Domain (members/events/communications/finance/projects): ").strip()
            insight = get_cached_insight(domain)
            if insight:
                print(f"\nCached Insight:\n{insight}")
            else:
                print("No cached insight yet. Run refresh first.")
        
        elif choice == "3":
            print("Goodbye.")
            break

if __name__ == "__main__":
    main()