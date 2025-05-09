import os
from search_news import get_latest_ai_news
from summarize_news import summarize_article
from post_to_blogger import post_article
from gist_utils import load_posted_urls_from_gist, save_posted_urls_to_gist

def main():
    articles = get_latest_ai_news()
    posted_urls = load_posted_urls_from_gist()

    for article in articles:
        if article["url"] in posted_urls:
            print(f"🟡 スキップ: {article['title']}")
            continue

        print(f"🟢 投稿: {article['title']}")
        summary = summarize_article(article['content'])
        post_article(title=article['title'], content=summary, url=article['url'])

        posted_urls.add(article["url"])
        save_posted_urls_to_gist(posted_urls)
        break

if __name__ == "__main__":
    main()
