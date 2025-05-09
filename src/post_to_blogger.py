
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def post_article(title, content, url):
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get("BLOGGER_REFRESH_TOKEN"),
        client_id=os.environ.get("BLOGGER_CLIENT_ID"),
        client_secret=os.environ.get("BLOGGER_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )

    service = build("blogger", "v3", credentials=creds)
    blogs = service.blogs().listByUser(userId="self").execute()
    blog_id = blogs["items"][0]["id"]

    post = {
        "title": title,
        "content": content + f"<br><br><a href='{url}'>[元記事リンク]</a>"
    }
    service.posts().insert(blogId=blog_id, body=post).execute()
