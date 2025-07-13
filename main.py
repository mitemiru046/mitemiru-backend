from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os, random, requests

# 環境変数読み込み
load_dotenv(Path(__file__).parent / ".env")
TMDB_KEY = os.getenv("TMDB_KEY")

app = FastAPI()

# CORS （ローカルと本番両方からOKに）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "https://axiomatic-trip-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 追加 ───
# frontend フォルダを /static 以下で配信
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
# ───────────

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/recommend")
def recommend():
    url = (
        "https://api.themoviedb.org/3/trending/movie/day"
        f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    movie = random.choice(requests.get(url, timeout=10).json()["results"])
    return {"title": movie["title"]}
    