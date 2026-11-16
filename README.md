# Pairwise YouTube Annotator

A lightweight web app for pairwise video labeling and comparison. Videos pairs are generated randomly drawing IDs from the `video_ids.json` file. Results are saved to an sqlite database.

![Screenshot](data/example.png)

## Quick Start

### 1. Prerequisites
Ensure you have [uv](https://docs.astral.sh/uv/) installed.

### 2. Install dependencies
```bash
uv sync
```

### 3. Run Locally
Start the FastAPI server:
```bash
uv run fastapi dev src/main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---




