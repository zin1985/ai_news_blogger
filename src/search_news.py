import os
import requests
from bs4 import BeautifulSoup

def get_page_text(url):
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        # 本文らしき段落を抽出
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return "\n".join(paragraphs[:10])  # 最初の10段落をまとめる
    except Exception as e:
        print(f"⚠️ {url} の取得に失敗しました:", e)
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
