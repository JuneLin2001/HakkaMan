from crawler import PTTCrawler, format_articles
from datetime import datetime
from zoneinfo import ZoneInfo
from line import LineBot


today_tw = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y/%m/%d")


def main():
    crawler = PTTCrawler("Lifeismoney")
    bot = LineBot()
    articles = crawler.crawl_board()

    if not articles:
        print("No articles found.")
        return

    message = f"📢 PTT 省錢版 {today_tw} 近兩天消息\n\n" + \
        format_articles(articles)

    # LINE message limit is 5000 chars
    if len(message) > 5000:
        message = message[:4997] + "..."
    bot.send_message(message)


if __name__ == "__main__":
    main()
