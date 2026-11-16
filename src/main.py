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
import pandas as pd

BASE_DIR = Path(__file__).parents[1]
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "data/annotations.db"
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            coder_id TEXT,
            session_id TEXT,
            video_a TEXT,
            video_b TEXT,
            winner TEXT,
            question TEXT
        )
    """)
    # Ensure coder_id exists if table was previously initialized without it
    existing_cols = [c[1] for c in conn.execute("PRAGMA table_info(annotations);").fetchall()]
    if "coder_id" not in existing_cols:
        conn.execute("ALTER TABLE annotations ADD COLUMN coder_id TEXT;")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTION = "Which video is more {X} leaning?"
CHOICES = ["right", "left"]

video_df = pd.read_csv(BASE_DIR / "data/video_ids.csv", index_col=0).fillna("")
video_ids = video_df.index.to_list()

@app.get("/fetch_pair")
def fetch_pair(lean: str = "right"):
    chosen_lean = lean.lower() if lean.lower() in CHOICES else "right"

    video_a = random.choice(video_ids)
    video_b = random.choice([vid for vid in video_ids if vid != video_a])
    metadata_a = video_df.loc[video_a]
    metadata_b = video_df.loc[video_b]

    question = QUESTION.format(X=chosen_lean)
    return {
        "video_a": video_a,
        "video_a_title": str(metadata_a["title"]),
        "video_a_channel": str(metadata_a["channel"]),
        "video_a_channel_id": str(metadata_a["channel_id"]),
        "video_a_description": str(metadata_a["description"]),
        "video_a_tags": str(metadata_a["tags"]),
        "video_b": video_b,
        "video_b_title": str(metadata_b["title"]),
        "video_b_channel": str(metadata_b["channel"]),
        "video_b_channel_id": str(metadata_b["channel_id"]),
        "video_b_description": str(metadata_b["description"]),
        "video_b_tags": str(metadata_b["tags"]),
        "question": question,
        "lean": chosen_lean
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
    coder_id: str
    session_id: str
    video_a: str
    video_b: str
    winner: str
    question: str

@app.post("/submit")
def submit(data: Submission):
    if data.code != os.getenv("CODE"):
        raise HTTPException(status_code=401, detail="Invalid access code")
    if not data.coder_id.strip():
        raise HTTPException(status_code=400, detail="Coder ID is required")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO annotations (coder_id, session_id, video_a, video_b, winner, question) VALUES (?, ?, ?, ?, ?, ?)",
            (data.coder_id, data.session_id, data.video_a, data.video_b, data.winner, data.question),
        )
    return {"status": "ok"}

app.mount("/", StaticFiles(directory=BASE_DIR / "src", html=True), name="static")

