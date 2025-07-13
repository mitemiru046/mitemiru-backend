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

# 健康チェック
@app.get("/health")
def health():
    return {"status": "ok"}

# 推薦エンドポイント
@app.get("/recommend")
 def recommend(period: Optional[str] = "day", query: Optional[str] = None):
-    # キーワード検索／トレンド取得の URL を組み立て…
+    # TMDB のトレンドは day/week のみ → month が来たら week にフォールバック
+    if period not in ("day", "week"):
+        period = "week"

     if query:
         # キーワード検索…
     else:
-        url = (
-            f"https://api.themoviedb.org/3/trending/movie/{period}"
-            f"?api_key={TMDB_KEY}&language=ja-JP"
-        )
+        url = (
+            f"https://api.themoviedb.org/3/trending/movie/{period}"
+            f"?api_key={TMDB_KEY}&language=ja-JP"
+        )
        results = requests.get(url, timeout=10).json().get("results", [])

    if not results:
        return {"id": None, "title": "該当する映画がありません"}
    movie = random.choice(results)
    return {"id": movie.get("id"), "title": movie.get("title")}

# 作品詳細取得エンドポイント
@app.get("/movie/{movie_id}")
def movie_detail(movie_id: int):
    """
    movie_id から TMDB の詳細情報を取りに行きます
    """
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={TMDB_KEY}&language=ja-JP"
    )
    data = requests.get(url, timeout=10).json()
    return {
        "title": data.get("title"),
        "overview": data.get("overview"),
        "rating": data.get("vote_average"),
        # フル URL にしておく
        "poster_url": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
    }