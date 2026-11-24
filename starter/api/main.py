"""Milestones 5-6: text-to-SQL + FastAPI. Run: uvicorn main:app --reload --port 8000 (from starter/api)"""
import os, re, psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import chat
load_dotenv()
app = FastAPI(title="Gift and Bliss Supplies - Ask")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

def schema_text() -> str:
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute("SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY 1, ordinal_position")
        out = {}
        for t, col, typ in cur.fetchall(): out.setdefault(t, []).append(f"{col} {typ}")
    return "\n".join(f"{t}({', '.join(c)})" for t, c in out.items())

# The AI's instructions: a short fixed intro plus YOUR business rules from Milestone 5.
# This is your business context layer. Edit business_rules.md, save, and the API uses it on the next question.
def business_rules() -> str:
    path = os.path.join(os.path.dirname(__file__), "business_rules.md")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()

SYSTEM = "You write PostgreSQL SELECT queries. Return only SQL, no explanation.\nSchema:\n{schema}\n\nBusiness rules. Follow them:\n{rules}"

def generate_sql(question: str) -> str:
    sql = chat([{"role": "system", "content": SYSTEM.format(schema=schema_text(), rules=business_rules())}, {"role": "user", "content": question}])
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.M).strip()

def run_sql(sql, max_rows=500):
    s = sql.strip().rstrip(";")
    if not re.match(r"(?is)^(select|with)\b", s) or ";" in s:
        raise ValueError("Only a single SELECT is allowed.")
    with psycopg2.connect(os.environ["READER_URL"]) as c, c.cursor() as cur:
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute("SET LOCAL statement_timeout = 5000")
        cur.execute(s)
        cols = [d[0] for d in cur.description]
        return cols, [list(r) for r in cur.fetchmany(max_rows)]

class Ask(BaseModel):
    question: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/ask")
def ask(body: Ask):
    sql = generate_sql(body.question)
    if sql.strip() == "CANNOT_ANSWER":
        return {"sql": "", "columns": [], "rows": [], "error": "I can't answer that from this data. Try asking about sales, profit, orders, returns or regions."}
    try:
        cols, rows = run_sql(sql)
        return {"sql": sql, "columns": cols, "rows": rows, "error": None}
    except Exception as e:
        return {"sql": sql, "columns": [], "rows": [], "error": str(e).splitlines()[0]}
