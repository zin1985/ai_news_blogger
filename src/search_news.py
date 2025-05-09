import os
import requests
from bs4 import BeautifulSoup

def get_page_text(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200 or len(res.text) < 500:
            print(f"⚠️ 無効または短すぎるページ: {url}")
            return ""

        soup = BeautifulSoup(res.text, "html.parser")

        # 本文抽出：pタグ → article内のテキスト → fallback
        paragraphs = soup.find_all("p")
        if not paragraphs:
            paragraphs = soup.select("article p")
        if not paragraphs:
            paragraphs = soup.find_all("div")

        text = "\n".join(p.get_text() for p in paragraphs)
        return text.strip()

    except Exception as e:
        print(f"⚠️ {url} の取得エラー:", e)
        return ""

def get_latest_ai_news():
    api_key = os.environ.get("SEARCH_API_KEY")
    engine_id = os.environ.get("SEARCH_ENGINE_ID")
    query = "AI news site:news.google.com"

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={engine_id}"
    res = requests.get(url)
    if res.status_code != 200:
        print("❌ Search API エラー:", res.status_code)
        return []

    items = res.json().get("items", [])
    print(f"🔍 検索結果件数: {len(items)}")

    results = []
    for item in items:
        article_url = item["link"]
        title = item["title"]
        full_text = get_page_text(article_url)

        if not full_text.strip():
            print(f"⚠️ {title} は本文取得できずスキップ")
            continue

        results.append({
            "title": title,
            "url": article_url,
            "content": full_text
        })

    return results
