
from search_news import get_latest_ai_news
from post_to_blogger import post_article
import time
from datetime import datetime

def post_article(title, content, url):
    print(f"📤 投稿: {title}\nURL: {url}\n内容（省略）")

def main():
    print("🔄 処理開始: ", datetime.now())
    total_start = time.time()

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
