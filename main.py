from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os, random, requests

# .env を読み込む
load_dotenv(Path(__file__).parent / ".env")
TMDB_KEY = os.getenv("TMDB_KEY")

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/recommend")
def recommend():
    url = (
        f"https://api.themoviedb.org/3/trending/movie/day"
        f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    movie = random.choice(requests.get(url, timeout=10).json()["results"])
    return {"title": movie["title"]}
    