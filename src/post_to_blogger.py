import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_keywords_from_text(text):
    prompt = (
        "Extract 3 to 5 relevant natural keywords from the following Japanese text. "
        "Return them in one line, separated by commas (e.g., AI, 環境, 思考力).\n\n" + text
    )
    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt + "\n\n" + text}]
        )
        raw = res.choices[0].message.content.strip()
        keywords = [kw.strip() for kw in raw.replace("・", ",").split(",") if kw.strip()]
        return keywords
    except Exception as e:
        print(f"⚠️ キーワード抽出失敗: {e}")
        return ["AI", "ニュース"]

def get_blogger_service():
    creds = Credentials.from_authorized_user_info({
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "token_uri": "https://oauth2.googleapis.com/token"
    }, scopes=["https://www.googleapis.com/auth/blogger"])
    return build('blogger', 'v3', credentials=creds)

def trim_labels_to_fit(labels, max_total_length=200):
    result = []
    total = 0
    for label in labels:
        length = len(label.encode("utf-8"))
        if total + length + 2 > max_total_length:  # +2 for separator margin
            break
        result.append(label)
        total += length
    return result

def post_article(title, content, url):
    service = get_blogger_service()
    blog_id = os.environ.get("BLOG_ID")

    # キーワード抽出（絵文字含む本文で）
    keywords = extract_keywords_from_text(content)
    labels = list(set(keywords + ["委員長ちゃん"]))
    labels = trim_labels_to_fit(labels)  # ←ここで制限！

    post = {
        "title": title,
        "content": content,
        "labels": labels
    }

    try:
        # 安全なJSON変換（エスケープ抑制）
        print("📤 投稿データ:", json.dumps(post, ensure_ascii=False, indent=2))

        result = service.posts().insert(blogId=blog_id, body=post, isDraft=False).execute()
        print(f"✅ 投稿成功: {result['url']}")
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
