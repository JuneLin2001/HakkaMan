"""
PTT Lifeismoney Board Web Crawler
Crawls articles from https://www.ptt.cc/bbs/Lifeismoney/
"""

import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime, timedelta


class PTTCrawler:
    def __init__(self, board_name: str = "Lifeismoney"):
        self.base_url = "https://www.ptt.cc"
        self.board_name = board_name
        self.board_url = f"{self.base_url}/bbs/{board_name}/index.html"

    def fetch_page(self, url: str) -> str:
        """Fetch a page from PTT"""
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.text

    def parse_article_list(self, html: str) -> List[Dict]:
        """Parse article list from board index page"""
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Find all article entries
        for entry in soup.find_all("div", class_="r-ent"):
            article = {}

            # Title and link
            title_tag = entry.find("div", class_="title")
            if title_tag and title_tag.find("a"):
                article["title"] = title_tag.find("a").text.strip()
                article["link"] = self.base_url + title_tag.find("a")["href"]
            else:
                # Post was deleted or no link
                article["title"] = title_tag.text.strip(
                ) if title_tag else "N/A"
                article["link"] = None

            # Push count (popularity)
            push_tag = entry.find("div", class_="nrec")
            article["push_count"] = push_tag.text.strip() if push_tag else "0"

            # Author
            author_tag = entry.find("div", class_="author")
            article["author"] = author_tag.text.strip() if author_tag else "N/A"

            # Date
            date_tag = entry.find("div", class_="date")
            article["date"] = date_tag.text.strip() if date_tag else "N/A"

            articles.append(article)

        return articles

    def get_previous_page_url(self, html: str) -> str:
        """Extract previous page URL from current page"""
        soup = BeautifulSoup(html, "html.parser")
        prev_link = soup.find("a", string="‹ 上頁")
        if prev_link and "href" in prev_link.attrs:
            return self.base_url + prev_link["href"]
        return None

    def crawl_board(self, num_pages: int = 1) -> List[Dict]:
        """Crawl multiple pages from the board"""
        all_articles = []
        current_url = self.board_url

        for page_num in range(num_pages):
            print(f"Crawling page {page_num + 1}/{num_pages}: {current_url}")

            try:
                html = self.fetch_page(current_url)
                articles = self.parse_article_list(html)
                all_articles.extend(articles)

                print(f"  Found {len(articles)} articles")

                # Get previous page URL for next iteration
                if page_num < num_pages - 1:
                    current_url = self.get_previous_page_url(html)
                    if not current_url:
                        print("  No more pages available")
                        break

            except Exception as e:
                print(f"  Error crawling page: {e}")
                break

        return all_articles

    def fetch_article_content(self, article_url: str) -> Dict:
        """Fetch full article content"""
        try:
            html = self.fetch_page(article_url)
            soup = BeautifulSoup(html, "html.parser")

            # Main content
            main_content = soup.find("div", id="main-content")
            if not main_content:
                return {"error": "Content not found"}

            # Extract metadata
            meta_lines = main_content.find_all(
                "span", class_="article-meta-value")
            metadata = {
                "author": meta_lines[0].text.strip() if len(meta_lines) > 0 else "N/A",
                "board": meta_lines[1].text.strip() if len(meta_lines) > 1 else "N/A",
                "title": meta_lines[2].text.strip() if len(meta_lines) > 2 else "N/A",
                "time": meta_lines[3].text.strip() if len(meta_lines) > 3 else "N/A",
            }

            # Extract main text (remove metadata and push tags)
            for meta in main_content.find_all("div", class_="article-metaline"):
                meta.decompose()
            for meta in main_content.find_all("div", class_="article-metaline-right"):
                meta.decompose()
            for push in main_content.find_all("div", class_="push"):
                push.decompose()

            content_text = main_content.get_text().strip()

            # Extract push/comments
            pushes = []
            for push_tag in soup.find_all("div", class_="push"):
                push_type = push_tag.find("span", class_="push-tag")
                push_user = push_tag.find("span", class_="push-userid")
                push_content = push_tag.find("span", class_="push-content")
                push_time = push_tag.find("span", class_="push-ipdatetime")

                pushes.append({
                    "type": push_type.text.strip() if push_type else "",
                    "user": push_user.text.strip() if push_user else "",
                    "content": push_content.text.strip() if push_content else "",
                    "time": push_time.text.strip() if push_time else ""
                })

            return {
                "metadata": metadata,
                "content": content_text,
                "pushes": pushes,
                "url": article_url
            }

        except Exception as e:
            return {"error": str(e)}


def format_articles(articles):
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    today = f"{now.month}/{now.day}"
    yesterday_str = f"{yesterday.month}/{yesterday.day}"
    filter_keywords = ['[集中]', '[公告]', '[協尋]', '[轉錄]', '[刪除]']

    today_articles = []
    for article in articles:
        if not article["link"]:
            continue

        if article["date"].strip() != today and article["date"].strip() != yesterday_str:
            continue

        if any(keyword in article['title'] for keyword in filter_keywords):
            continue

        today_articles.append(article)

    def get_push_value(article):
        push = article["push_count"].strip()
        if push == "爆":
            return 1000
        elif push == "" or push == "0":
            return 0
        else:
            try:
                return int(push)
            except:
                return 0

    today_articles.sort(key=get_push_value, reverse=True)

    today_lines = []
    for article in today_articles:
        push = article["push_count"] or "0"
        today_lines.append(
            f"[{push} 推] {article['title']} \n{article['link']}")

    return "\n\n".join(today_lines)
