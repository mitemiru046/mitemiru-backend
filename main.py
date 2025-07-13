from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os, random, requests

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

# 既存の /health と /recommend はそのまま
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