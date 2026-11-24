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

# BASELINE prompt: schema only. It knows nothing about the business. That is on purpose.
# TODO (M5): improve it with what YOU learned in M1-M2 (cleaning rules, definitions, fiscal year...).
SYSTEM = "You write PostgreSQL SELECT queries. Return only SQL, no explanation.\nSchema:\n{schema}"

def generate_sql(question: str) -> str:
    sql = chat([{"role": "system", "content": SYSTEM.format(schema=schema_text())}, {"role": "user", "content": question}])
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.M).strip()

def run_sql(sql: str, max_rows=500):
    # TODO (M6): make this safe: SELECT-only guard, statement timeout, read-only role.
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return cols, [list(r) for r in cur.fetchmany(max_rows)]

class Ask(BaseModel):
    question: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/ask")
def ask(body: Ask):
    sql = generate_sql(body.question)
    try:
        cols, rows = run_sql(sql)
        return {"sql": sql, "columns": cols, "rows": rows, "error": None}
    except Exception as e:
        return {"sql": sql, "columns": [], "rows": [], "error": str(e).splitlines()[0]}
