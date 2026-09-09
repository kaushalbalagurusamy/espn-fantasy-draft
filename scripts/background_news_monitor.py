import time
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.injury_news_sync import sync_injuries_and_news

def run_monitor(interval_seconds=60):
    print(f"Starting Background NFL Injury & News Monitor (Interval: {interval_seconds}s)...", flush=True)
    while True:
        try:
            alerts = sync_injuries_and_news()
            if alerts:
                print(f"[{alerts['last_updated']}] Live Sync: {alerts['out_count']} OUT | {alerts['ir_count']} IR/PUP | {len(alerts['breaking_news'])} News Items", flush=True)
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Live Sync completed.", flush=True)
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sync error: {e}", flush=True)
            
        time.sleep(interval_seconds)

if __name__ == "__main__":
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    run_monitor(interval)
