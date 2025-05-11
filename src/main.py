
from search_news import get_latest_ai_news
from post_to_blogger import post_article
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from openai import OpenAI
import os
import time

def check_blogger_api():
    try:
        creds = Credentials.from_authorized_user_info({
            "client_id": os.environ["BLOGGER_CLIENT_ID"],
            "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
            "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
            "token_uri": "https://oauth2.googleapis.com/token"
        }, scopes=["https://www.googleapis.com/auth/blogger"])

        service = build('blogger', 'v3', credentials=creds)
        # 軽いテスト：自分のブログ情報取得
        blog_id = os.environ.get("BLOG_ID")
        blog = service.blogs().get(blogId=blog_id).execute()
        print(f"✅ Blogger API認証成功: {blog.get('name')}")
        return True
    except Exception as e:
        print(f"❌ Blogger API認証失敗: {e}")
        return False

def check_openai_api_key():
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        print("✅ ChatGPT APIキーは有効です")
        return True
    except Exception as e:
        print(f"❌ ChatGPT APIキー確認失敗: {e}")
        return False

def validate_before_processing():
    if not check_blogger_api():
        print("🚫 Blogger API認証に失敗しました。処理を中止します。")
        return False
    if not check_openai_api_key():
        print("🚫 OpenAI APIキーが無効です。処理を中止します。")
        return False
    return True
    
def main():
    print("🔄 処理開始: ", datetime.now())
    total_start = time.time()

    print("🔍 API利用チェック...")
    if not validate_before_processing():
        return    
    
    print("🔍 AIニュース取得中...")
    start = time.time()
    articles = get_latest_ai_news()
    print(f"✅ ニュース取得完了：{len(articles)}件（{time.time() - start:.1f}秒）")

    for article in articles:
        print(f"📝 投稿開始: {article['title']}")
        post_start = time.time()
        post_article(title=article['title'], content=article['content'], url=article['url'])
        print(f"✅ 投稿完了（{time.time() - post_start:.1f}秒）")

    print("🏁 全投稿完了")
    print(f"🕒 合計処理時間：{time.time() - total_start:.1f}秒")

if __name__ == "__main__":
    main()
