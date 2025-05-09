import os
import requests

def get_latest_ai_news():
    api_key = os.environ.get("SEARCH_API_KEY")
    engine_id = os.environ.get("SEARCH_ENGINE_ID")
    query = "AI news site:news.google.com"  # ← 必要に応じて調整

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={engine_id}"
    res = requests.get(url)

    if res.status_code != 200:
        print("❌ Search API 失敗:", res.status_code)
        print("レスポンス:", res.text)
        return []

    data = res.json()

    # 🔍 デバッグ出力：レスポンス全体の構造確認
    print("🔎 Search API レスポンス全体:", data)

    items = data.get("items", [])
    print(f"🔍 検索結果件数: {len(items)}")

    return [{"title": item["title"], "url": item["link"], "content": item.get("snippet", "")} for item in items]
