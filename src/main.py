from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import random
import json
from dotenv import load_dotenv
import os
import uuid
import sqlite3

BASE_DIR = Path(__file__).parents[1]
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "data/annotations.db"
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            video_a TEXT,
            video_b TEXT,
            winner TEXT,
            question TEXT
        )
    """)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION = "Which video is more {X} leaning?"
CHOICES = ["left", "right"]

with open(BASE_DIR / "data/video_ids.json", "r") as f:
    video_ids = json.load(f)

@app.get("/fetch_pair")
def fetch_pair():
    video_a = random.choice(video_ids)
    video_b = random.choice([vid for vid in video_ids if vid != video_a])
    question = QUESTION.format(X=random.choice(CHOICES))
    return {
        "video_a": video_a,
        "video_b": video_b,
        "question": question
    }

@app.post("/validate_code")
def validate_code(code: str):
    if code == os.getenv("CODE"):
        return {"valid": True}
    return {"valid": False}

@app.get("/get_session_id")
def get_session_id():
    return {"session_id": str(uuid.uuid4())}

class Submission(BaseModel):
    code: str
    video_a: str
    video_b: str
    winner: str
    question: str
    session_id: str

@app.post("/submit")
def submit(data: Submission):
    if data.code != os.getenv("CODE"):
        raise HTTPException(status_code=401, detail="Invalid access code")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO annotations (session_id, video_a, video_b, winner, question) VALUES (?, ?, ?, ?, ?)",
            (data.session_id, data.video_a, data.video_b, data.winner, data.question),
        )
    return {"status": "ok"}

app.mount("/", StaticFiles(directory=BASE_DIR / "src", html=True), name="static")

