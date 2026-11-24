"""Milestone 5 helper: pull a challenge set from the course server, run YOUR text-to-SQL on each question, submit the SQL.
The server runs your SQL on its own copy of the data and tells you which questions passed. Answers are never shown."""
import os, sys, json, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "starter", "api"))
from main import generate_sql
BASE = os.environ.get("GBS_COURSE_API", "https://cvfine.com/api")  # set when the course server is live
TOKEN = os.environ["GBS_TOKEN"]  # shown in your cvfine.com project page
H = {"Authorization": f"Bearer {TOKEN}"}
qs = requests.get(f"{BASE}/v1/gbs/challenge", headers=H, timeout=30).json()["questions"]
answers = [{"id": q["id"], "sql": generate_sql(q["text"])} for q in qs]
print(json.dumps(requests.post(f"{BASE}/v1/gbs/challenge/submit", headers=H, json={"answers": answers}, timeout=60).json(), indent=2))
