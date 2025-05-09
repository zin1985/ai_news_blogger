import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
from search_news_util import rewrite_with_comments, insert_html_wrappers, translate_title_to_japanese

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

def get_page_text_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.binary_location = "/usr/bin/chromium-browser"
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p, article, div[data-testid='Body']"))
        )

        paragraphs = driver.find_elements(By.CSS_SELECTOR, "p, div[data-testid='Body'] div, article p")
        text = "\\n".join([p.text for p in paragraphs if p.text.strip()])
        short_text = text.strip()[:4000]
        print("📄 取得した本文プレビュー（先頭200文字）:")
        print(short_text[:200] + "..." if len(short_text) > 200 else short_text)
        return short_text
    except Exception as e:
        print(f"⚠️ Selenium取得失敗: {e}")
        return ""
    finally:
        driver.quit()

def get_latest_ai_news():
    query = "OpenAI FDA AI site:reuters.com OR site:cnn.com OR site:nytimes.com OR site:bbc.com"
    url = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"

    try:
        res = requests.get(url)
        res.raise_for_status()
        items = res.json().get("items", [])
    except Exception as e:
        print(f"❌ Search API失敗: {e}")
        return []

    articles = []
    for item in items[:10]:
        title_en = item["title"]
        article_url = item["link"]
        print(f"🔗 URL取得: {article_url}")
        full_text = get_page_text_with_selenium(article_url)
        if not full_text or len(full_text) < 300:
            print(f"⚠️ 無効または短すぎるページ: {article_url}")
            continue
        rewritten = rewrite_with_comments(full_text)
        wrapped = insert_html_wrappers(title_en, article_url, rewritten)
        title_ja = translate_title_to_japanese(title_en)
        final_title = f"『{title_ja}』を委員長ちゃんが解説♪"
        articles.append({
            "title": final_title,
            "url": article_url,
            "content": wrapped
        })

    return articles
