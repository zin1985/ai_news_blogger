import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_keywords_from_text(text):
    prompt = (
        "以下の日本語の文章から、内容に関連する自然なキーワードを3〜5個、日本語で抽出してください。"
        "箇条書きや番号なしで、カンマ区切りで出力してください：\\n\\n" + text
    )
    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        keywords = res.choices[0].message.content.strip()
        return [kw.strip() for kw in keywords.split(",") if kw.strip()]
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

def post_article(title, content, url):
    service = get_blogger_service()
    blog_id = os.environ.get("7990898328410672454")

    keywords = extract_keywords_from_text(content)
    labels = list(set(keywords + ["委員長ちゃん"]))

    post = {
        "title": title,
        "content": content,
        "labels": labels
    }

    try:
        result = service.posts().insert(blogId=blog_id, body=post, isDraft=False).execute()
        print(f"✅ 投稿成功: {result['url']}")
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
