from search_news import get_latest_ai_news
from summarize_news import summarize_article
from post_to_blogger import post_article

def main():
    articles = get_latest_ai_news()
    for article in articles[:1]:
        summary = summarize_article(article['content'])
        post_article(title=article['title'], content=summary, url=article['url'])

if __name__ == "__main__":
    main()
