
import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
        time.sleep(3)
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        text = "\n".join([p.text for p in paragraphs])
        return text.strip()[:4000]
    except Exception as e:
        print(f"⚠️ Selenium取得失敗: {e}")
        return ""
    finally:
        driver.quit()

def detect_emotion(comment):
    prompt = f"以下の日本語の文から、感情を1単語で英語で分類してください（happy, angry, sad, surprised, confused, love, neutralのいずれか）。感情名だけを出力してください：\n\n\"{comment}\""
    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        emotion = res.choices[0].message.content.strip().lower()
        return emotion if emotion in ["happy", "angry", "sad", "surprised", "confused", "love", "neutral"] else "neutral"
    except Exception as e:
        print(f"⚠️ 感情判定スキップ: {e}")
        return "neutral"

# ...（略）その他の処理（translate_title_to_japanese, rewrite_with_comments 等はそのまま）


# 省略部分にあたる関数もこのあと補完する形で構成されています。
