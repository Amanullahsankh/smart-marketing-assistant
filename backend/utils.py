import logging
import json, os

logger = logging.getLogger(__name__)

SEEN_FILE = "seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        return set(json.load(open(SEEN_FILE)))
    return set()

def save_seen(seen):
    json.dump(list(seen), open(SEEN_FILE, "w"))

def add_and_check(link):
    seen = load_seen()
    if link in seen:
        return False
    seen.add(link)
    save_seen(seen)
    return True
