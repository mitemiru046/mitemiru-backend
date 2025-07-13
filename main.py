from fastapi import FastAPI, Request, HTTPException
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

# ① frontend フォルダを静的ファイルとして公開
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "frontend" / "frontend"),
    name="static",
)

# ② ルートにアクセスが来たら index.html を返す
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = Path(__file__).parent / "frontend" / "frontend" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))

# 既存の /health はそのまま
@app.get("/health")
def health():
    return {"status": "ok"}

# /recommend?period=day|week|month&query=キーワード
@app.get("/recommend")
def recommend(
    period: Optional[str] = "day",
    query: Optional[str] = None
):
    if query:
        # キーワード検索
        url = (
            "https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_KEY}&language=ja-JP&query={query}"
        )
    else:
        # トレンド取得
        if period not in ("day", "week", "month"):
            raise HTTPException(status_code=400, detail="period must be day/week/month")
        url = (
            f"https://api.themoviedb.org/3/trending/movie/{period}"
            f"?api_key={TMDB_KEY}&language=ja-JP"
        )

    resp = requests.get(url, timeout=10)
    data = resp.json().get("results")
    if not data:
        raise HTTPException(status_code=404, detail="no movies found")
    movie = random.choice(data)
    # 映画 ID も返す
    return {"id": movie["id"], "title": movie["title"]}

# /movie/{movie_id} で詳細を返す
@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="movie not found")
    info = resp.json()
    return {
        "id": info["id"],
        "title": info["title"],
        "overview": info.get("overview", ""),
        "rating": info.get("vote_average", 0),
        # フル URL を組み立てる
        "poster_url": f"https://image.tmdb.org/t/p/w300{info.get('poster_path', '')}"
    }