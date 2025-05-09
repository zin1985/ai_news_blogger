
import os
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_page_text_with_selenium(url):
    options = Options()
    options.add_argument("--disable-software-rasterizer")
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(3)
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        text = "\n".join([p.text for p in paragraphs])
        return text.strip()
    except Exception as e:
        print(f"⚠️ Selenium取得失敗: {e}")
        return ""
    finally:
        driver.quit()

def detect_emotion(comment):
    prompt = f"以下の日本語の文から、感情を1単語で英語で分類してください（happy, angry, sad, surprised, confused, love, neutralのいずれか）。感情名だけを出力してください：\n\n"{comment}""
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    emotion = res.choices[0].message.content.strip().lower()
    return emotion if emotion in ["happy", "angry", "sad", "surprised", "confused", "love", "neutral"] else "neutral"

def insert_emotion_images(text):
    # コメント行の後に画像を挿入（例：> 💬 コメント の直後）
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("> 💬"):
            emotion = detect_emotion(line)
            new_lines.append(f"![](images/{emotion}.png)")
    return "\n".join(new_lines)

def get_latest_ai_news():
    api_key = os.environ.get("SEARCH_API_KEY")
    engine_id = os.environ.get("SEARCH_ENGINE_ID")
    query = "AI site:techcrunch.com OR site:wired.com OR site:itmedia.co.jp"

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
        full_text = get_page_text_with_selenium(article_url)
        if not full_text.strip():
            print(f"⚠️ {title} は本文取得できずスキップ")
            continue

        rewritten_with_comments = rewrite_with_comments(full_text)
        combined = insert_emotion_images(rewritten_with_comments)

        results.append({
            "title": title,
            "url": article_url,
            "content": combined
        })

    return results

def rewrite_with_comments(text):
    prompt = f"""
以下は英語のウェブ記事本文です。これを以下のように日本語で変換してください：

【変換ルール】
1. 全体を要約せず、1センテンスずつ丁寧に翻訳・言い換えてください。
2. 各センテンスの直後に「AI学級委員長ちゃん」としてのコメントを1文挿入してください。
3. コメントの前には必ず「> 💬 」という記号を付けてください。
4. コメントはややツンデレ気味で、かわいくて面倒見が良く、優しい感じにしてください。
5. コメントは鋭く本質を突くこともあるが、根本的には励まし・共感・優しさのある内容にしてください。
6. 全体は学級委員長キャラが記事を読んでいるような口調と雰囲気にしてください。

【キャラ設定】
- 一人称：「わたし」
- 口調：基本は丁寧。近しい対象には砕けた口調で少し照れる
- 性格：優しく、面倒見が良いが、真面目でツンデレ気味
- 好きなもの：猫、ラーメン、箱庭系ゲーム
- イメージ：メガネの黒髪ポニテの女子学級委員長（ジト目気味）

--- 英文本文 ---
{text}
--- ここまで ---

それでは、本文を日本語に変換して、委員長ちゃんのコメント付きで出力してください。
"""
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはメガネの黒髪ポニーテールのAI学級委員長ちゃんです。優しく真面目で、時々ツンとするけど実はすごく面倒見がいいです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content.strip()
