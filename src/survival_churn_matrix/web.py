import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

app = FastAPI(title="SurvivalChurn Matrix")

class Database:
    def __init__(self, db_path: str = "survival_churn.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cohorts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    survival_rate REAL NOT NULL,
                    churn_rate REAL NOT NULL,
                    created_at TIMESTAMP
                )
            """)

    def add_cohort(self, name: str, survival: float, churn: float):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO cohorts VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), name, survival, churn, datetime.now().isoformat())
            )

    def get_all(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM cohorts ORDER BY created_at DESC")]

db = Database()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head><meta charset="UTF-8"><title>SurvivalChurn Matrix</title></head>
<body class="p-8 bg-zinc-950 text-white">
    <h1 class="text-2xl font-bold">SurvivalChurn Matrix</h1>
    <table class="w-full mt-4">
        {% for cohort in cohorts %}
        <tr><td>{{ cohort.name }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.get("/")
async def index():
    cohorts = db.get_all()
    return {"cohorts": cohorts}

@app.post("/cohorts", status_code=HTTP_303_SEE_OTHER)
async def create_cohort(name: str = Form(...), survival: float = Form(...), churn: float = Form(...)):
    db.add_cohort(name, survival, churn)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)