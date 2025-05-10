
import os
import requests
import time
import tempfile
import json
import random
from openai import OpenAI
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

def get_page_text_with_playwright(url):
    print(f"🌐 [Playwright] アクセス開始: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # ✅ モバイルブラウザ風の環境を構築（UA偽装＋viewport指定＋is_mobile）
            context = browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                           "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                           "Version/16.0 Mobile/15E148 Safari/604.1",
                viewport={"width": 375, "height": 667},
                is_mobile=True,
                device_scale_factor=2
            )

            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)  # JS描画の余裕を確保

            # ✅ モバイル表示では body の inner_text をまるごと取得
            content = page.inner_text("body")
            print(f"🧾 抽出文字数: {len(content)}\n{content[:300]}...")
            browser.close()
            return content.strip()[:4000]

    except Exception as e:
        print(f"⚠️ Playwright取得失敗: {e}")
        return ""

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
    
def get_random_site_query(keyword="OpenAI FDA AI", json_path="news_sources.json", k=3):
    with open(json_path, "r") as f:
        data = json.load(f)
        sources = data["sources"]
        selected = random.sample(sources, k=min(k, len(sources)))  # 最大k件ランダムに選択
        site_query = " OR ".join(f"site:{s}" for s in selected)
        return f"{keyword} {site_query}"

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
    query = get_random_site_query()  # ← 動的に検索クエリを生成（任意）
    url = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"

    try:
        res = requests.get(url)
        res.raise_for_status()
        items = res.json().get("items", [])
    except Exception as e:
        print(f"❌ Search API失敗: {e}")
        return []

    for item in items[:20]:
        title_en = item["title"]
        article_url = item["link"]
        print(f"🔗 URL取得: {article_url}")
        full_text = get_page_text_with_playwright(article_url)
        print(f"🔗 本文取得: {full_text}")
        if not full_text or len(full_text) < 300:
            print(f"⚠️ 無効または短すぎるページ: {article_url}")
            continue

        rewritten = rewrite_with_comments(full_text)
        wrapped = insert_html_wrappers(title_en, article_url, rewritten)
        title_ja = translate_title_to_japanese(title_en)
        final_title = f"『{title_ja}』を委員長ちゃんが解説♪"
        return [{
            "title": final_title,
            "url": article_url,
            "content": wrapped
        }]

    return []  # 1件も有効記事がなかった場合
