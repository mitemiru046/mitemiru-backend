from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os, random, requests

# .env を読み込む
load_dotenv(Path(__file__).parent / ".env")
TMDB_KEY = os.getenv("TMDB_KEY")

app = FastAPI()

# ① frontend を static で公開
app.mount(
  "/static",
  StaticFiles(directory=Path(__file__).parent / "frontend" / "frontend"),
  name="static",
)

# ② ルートに来たら index.html を返す
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html = (Path(__file__).parent / "frontend" / "frontend" / "index.html") \
           .read_text(encoding="utf-8")
    return HTMLResponse(html)

# 既存のヘルスチェック
@app.get("/health")
def health():
    return {"status": "ok"}

# ③ /recommend : period と query を受け取る
@app.get("/recommend")
def recommend(
    period: str = Query("day", regex="^(day|week|month)$"),
    query: str | None = Query(None, min_length=1),
):
    if query:
        # キーワード検索 API
        url = (
          f"https://api.themoviedb.org/3/search/movie"
          f"?api_key={TMDB_KEY}&language=ja-JP&query={query}"
        )
    else:
        # トレンド取得 API
        url = (
          f"https://api.themoviedb.org/3/trending/movie/{period}"
          f"?api_key={TMDB_KEY}&language=ja-JP"
        )

    results = requests.get(url, timeout=10).json().get("results", [])
    if not results:
        return {"id": None, "title": "該当なし", "overview": "", "rating": None, "poster_path": None}

    movie = random.choice(results)
    return {
      "id": movie["id"],
      "title": movie["title"],
      "overview": movie.get("overview",""),
      "rating": movie.get("vote_average"),
      "poster_path": movie.get("poster_path"),
    }

# ④ /movie/{id} : 詳細取得
@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    url = (
      f"https://api.themoviedb.org/3/movie/{movie_id}"
      f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    r = requests.get(url, timeout=10).json()
    return {
      "title": r.get("title",""),
      "overview": r.get("overview",""),
      "rating": r.get("vote_average"),
      "poster_path": r.get("poster_path"),
    }