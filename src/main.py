from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import random
import json
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).parents[1]
load_dotenv(BASE_DIR / ".env")

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
def validate_code(code : str):
    if code == os.getenv("CODE"):
        return {"valid": "True"}
    else:
        return {"valid": "False"}

app.mount("/", StaticFiles(directory=BASE_DIR / "src", html=True), name="static")

