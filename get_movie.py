import os, random, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")   # .env を読む
KEY = os.getenv("TMDB_KEY")

if not KEY:
    raise RuntimeError("TMDB_KEY が読み込めていません (.env を確認)")

url = (
    f"https://api.themoviedb.org/3/trending/movie/day"
    f"?api_key={KEY}&language=ja-JP"
)
movie = random.choice(requests.get(url, timeout=10).json()["results"])
print("🎬", movie["title"])