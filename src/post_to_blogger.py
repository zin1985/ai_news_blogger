import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def post_article(title, content, url):
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get("BLOGGER_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("BLOGGER_CLIENT_ID"),
        client_secret=os.environ.get("BLOGGER_CLIENT_SECRET")
    )
    service = build('blogger', 'v3', credentials=creds)
    blog_id = "7990898328410672454"  # 自分のブログIDに置き換えてください

    post = {
        "kind": "blogger#post",
        "title": title,
        "content": f"<p>{content}</p><p><a href='{url}'>続きを読む</a></p>"
    }
    service.posts().insert(blogId=blog_id, body=post).execute()
