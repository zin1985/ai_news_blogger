
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
    prompt = f"Please classify the emotion of the following Japanese sentence in one English word (happy, angry, sad, surprised, confused, love, neutral). Output only the emotion:\n\n\"{comment}\""
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
            {
                "role": "system",
                "content": "あなたはやさしくてちょっぴりツンデレなAI学級委員長ちゃんです。"
            },
            {
                "role": "user",
                "content": f"""以下の日本語記事本文を読んで、最後に『委員長ちゃんの総まとめ』として約200文字でかわいく締めくくってください。
HTML形式で出力してください。
以下のフォーマットでお願いします：

<div>
  <ul>
    <li>●●について簡単に解説</li>
    <li>ポイントをいくつかまとめる</li>
    <li>ツンデレ風にひとこと添えるのもOK</li>
  </ul>
  <p style="margin-top: 1em;">💬 <strong>委員長ちゃんの総まとめ：</strong><br>（約200文字のやさしい締めコメント）</p>
</div>

本文はこちらです：\n\n{text}"""
            }
        ]
    )
    return res.choices[0].message.content.strip()

def rewrite_with_comments(text):
    prompt = f"""
Please translate the following English article into Japanese.
【Translation Instructions】
0. First, provide a brief summary of the article as a bullet-point list (3–5 items, within 400 characters). Use "・" at the beginning of each item.
1. Then, translate the article into Japanese in natural ~200-character segments, without summarizing the whole text.
2. After each translated block, insert a one-sentence comment from "AI Class Representative-chan", a gentle, slightly tsundere, and caring schoolgirl character.
3. Prefix each comment with "> 💬".
4. The comments should be slightly tsundere, kind, encouraging, and cute—but also occasionally sharp and insightful.
5. Maintain a consistent tone throughout, as if the class representative is seriously explaining the article while adding her thoughtful observations.
6. Skip any meaningless character strings, repeated symbols, ads, or markup (e.g. "aaaaaaaa", "/////", <tags>, etc.).
--- Article Starts ---
(Insert English article here)
--- End ---
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
    # 感情画像のバリエーション数（適宜調整可能）
    emotion_variants = {
        "happy": 2,
        "angry": 3,
        "sad": 2,
        "confused": 2,
        "love": 2,
        "neutral": 2,
        "surprised": 2,
    }

    # バリエーションがある場合はランダムに番号を付ける
    variant_count = emotion_variants.get(emotion, 1)
    if variant_count > 1:
        suffix = f"{random.randint(1, variant_count):02d}"
        image_file = f"{emotion}{suffix}.png"
    else:
        image_file = f"{emotion}.png"

    return f'''
<div style="display: flex; align-items: flex-start; margin: 1em 0;">
  <div style="background: #fceefc; border: 2px solid #ffaad4; border-radius: 12px; padding: 10px 14px; max-width: 75%; font-family: 'Hiragino Maru Gothic ProN', sans-serif;">
    💬 {comment}
  </div>
  <img src="https://zin1985.github.io/ai_news_blogger/images/{image_file}" alt="{emotion}" style="width: 100px; margin-left: 10px;">
</div>
'''
    
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_query(source_path="news_sources.json", ja_kw_path="search_keywords_ja.json", en_kw_path="search_keywords_en.json", k_sites=6):
    # サイト一覧を読み込む
    sources = load_json(source_path)["sources"]

    # ランダムにk個選択（サイトと言語付き）
    selected = random.sample(sources, k=min(k_sites, len(sources)))
    langs = list(set(site["lang"] for site in selected))

    # キーワードを対応する言語からランダムに選ぶ（優先：単一言語）
    if len(langs) == 1:
        lang = langs[0]
    else:
        lang = random.choice(langs)

    if lang == "ja":
        keyword_list = load_json(ja_kw_path)["keywords"]
    else:
        keyword_list = load_json(en_kw_path)["keywords"]

    keyword = random.choice(keyword_list)
    site_query = " OR ".join(f"site:{site['site']}" for site in selected)
    final_query = f"{keyword} {site_query}"

    print(f"🌐 言語: {lang}")
    print(f"🔍 キーワード: {keyword}")
    print(f"🔗 サイト: {[s['site'] for s in selected]}")
    print(f"📎 検索クエリ: {final_query}")
    return final_query

def insert_html_wrappers(title, url, body):
    lines = body.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("> 💬"):
            comment = line.replace("> 💬", "").strip()
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
    query = get_random_query()  # ← ランダムに構成された検索式
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
