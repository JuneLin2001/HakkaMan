from crawler import PTTCrawler, format_articles
from datetime import datetime
from line import send_line_message


today_YYYYMMDD = datetime.now().strftime("%Y/%m/%d")


def main():
    crawler = PTTCrawler("Lifeismoney")
    articles = crawler.crawl_board()

    if not articles:
        print("No articles found.")
        return

    message = f"📢 PTT 省錢版 {today_YYYYMMDD} 近兩天消息\n\n" + \
        format_articles(articles)

    # LINE message limit is 5000 chars
    if len(message) > 5000:
        message = message[:4997] + "..."
    send_line_message(message)


if __name__ == "__main__":
    main()
