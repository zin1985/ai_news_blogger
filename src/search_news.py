import os
import requests

def get_latest_ai_news():
    api_key = os.environ.get("SEARCH_API_KEY")
    engine_id = os.environ.get("SEARCH_ENGINE_ID")
    query = "AI 最新ニュース"
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={engine_id}"
    res = requests.get(url)
    results = res.json().get("items", [])
    return [{"title": item["title"], "url": item["link"], "content": item.get("snippet", "")} for item in results]
