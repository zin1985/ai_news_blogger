
import os
import requests
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

def get_page_text_with_selenium(url):
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    import traceback

    options = Options()
    options.add_argument("--headless")  # ← new で落ちる場合は old headless に変更
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        print("🔧 STEP 1: Creating Chrome WebDriver instance...")
        driver = webdriver.Chrome(options=options)
        print("✅ STEP 1 OK: Chrome WebDriver started")

        print(f"🔧 STEP 2: Navigating to URL: {url}")
        driver.get(url)
        print("✅ STEP 2 OK: Page loaded")

        print("🔧 STEP 3: Waiting for <p> elements...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "p"))
        )

        print("🔧 STEP 4: Extracting text from <p> elements...")
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        text = "\n".join([p.text for p in paragraphs if p.text.strip()])
        print(f"🧾 抽出文字数: {len(text)}\n{text[:300]}...")
        return text.strip()[:4000]

    except Exception as e:
        print("⚠️ Selenium取得失敗（例外発生）:")
        traceback.print_exc()
        return ""

    finally:
        if driver:
            try:
                print("🔧 STEP 5: Quitting Chrome WebDriver...")
                driver.quit()
                print("✅ STEP 5 OK: Chrome WebDriver quit")
            except Exception as quit_err:
                print(f"⚠️ driver.quit() でエラー: {quit_err}")

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
        print(f"$26A0$FE0F 感情判定スキップ: {e}")
        return "neutral"

def translate_title_to_japanese(title):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"以下の英語タイトルを自然な日本語に翻訳してください：\n\n{title}"}]
    )
    return res.choices[0].message.content.strip()

def generate_summary_comment(text):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはやさしくてちょっぴりツンデレなAI学級委員長ちゃんです。"},
            {"role": "user", "content": f"以下の日本語記事本文を読んで、最後に『委員長ちゃんの総まとめ』として約400文字でかわいく締めくくってください。\n\n{text}"}
        ]
    )
    return res.choices[0].message.content.strip()

def rewrite_with_comments(text):
    prompt = f"""
以下は英語のウェブ記事本文です。これを以下のように日本語で変換してください：

【変換ルール】
1. 全体を要約せず、1センテンスずつ丁寧に翻訳・言い換えてください。
2. 各センテンスの直後に「AI学級委員長ちゃん」としてのコメントを1文挿入してください。
3. コメントの前には必ず「> $D83D$DCAC 」という記号を付けてください。
4. コメントはややツンデレ気味で、かわいくて面倒見が良く、優しい感じにしてください。
5. コメントは鋭く本質を突くこともあるが、根本的には励まし・共感・優しさのある内容にしてください。
6. 全体は学級委員長キャラが記事を読んでいるような口調と雰囲気にしてください。
"""
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはメガネの黒髪ポニーテールのAI学級委員長ちゃんです。"},
            {"role": "user", "content": prompt + "\n\n--- 英文本文 ---\n" + text + "\n--- ここまで ---"}
        ]
    )
    return res.choices[0].message.content.strip()

def format_comment_block(comment, emotion):
    return f'''
<div style="display: flex; align-items: flex-start; margin: 1em 0;">
  <div style="background: #fceefc; border: 2px solid #ffaad4; border-radius: 12px; padding: 10px 14px; max-width: 75%; font-family: 'Hiragino Maru Gothic ProN', sans-serif;">
    $D83D$DCAC {comment}
  </div>
  <img src="https://zin1985.github.io/ai_news_blogger/images/{emotion}.png" alt="{emotion}" style="width: 100px; margin-left: 10px;">
</div>
'''

def insert_html_wrappers(title, url, body):
    lines = body.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("> $D83D$DCAC"):
            comment = line.replace("> $D83D$DCAC", "").strip()
            emotion = detect_emotion(comment)
            new_lines.append(format_comment_block(comment, emotion))
        else:
            new_lines.append(f"<p>{line}</p>")
    summary = generate_summary_comment(body)
    new_lines.insert(0, f"<p>こんにちは、AI学級委員長ちゃんが今日もわかりやすく解説するね♪</p>")
    new_lines.insert(1, f"<p><strong>元記事URL：</strong> <a href='{url}' target='_blank'>{url}</a></p>")
    new_lines.append(f"<h3>委員長ちゃんの総まとめ</h3>")
    new_lines.append(f"<p>{summary}</p>")
    return "\n".join(new_lines)

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
        print(f"🔗 本文取得: {full_text}")
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
