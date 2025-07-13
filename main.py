from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os, random, requests
from typing import Optional

# .env を読み込む
load_dotenv(Path(__file__).parent / ".env")
TMDB_KEY = os.getenv("TMDB_KEY")

app = FastAPI()

# 静的ファイル
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "frontend" / "frontend"),
    name="static",
)

# フロントエンド
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = Path(__file__).parent / "frontend" / "frontend" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/recommend")
def recommend(period: Optional[str] = "day", query: Optional[str] = None):
    # ← この行と下の行のインデントを必ず揃えてください
    if period not in ("day", "week"):
        period = "week"

    if query:
        url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_KEY}&query={requests.utils.quote(query)}&language=ja-JP"
        )
    else:
        url = (
            f"https://api.themoviedb.org/3/trending/movie/{period}"
            f"?api_key={TMDB_KEY}&language=ja-JP"
        )

    movie = random.choice(requests.get(url, timeout=10).json().get("results", []))
    return {"id": movie["id"], "title": movie["title"]}

@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    data = requests.get(url, timeout=10).json()
    return {
        "title": data["title"],
        "overview": data.get("overview", ""),
        "rating": data.get("vote_average", 0),
        "poster_url": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
    }