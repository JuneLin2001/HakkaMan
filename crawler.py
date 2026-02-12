"""
PTT Lifeismoney Board RSS Crawler
Fetches articles from https://www.ptt.cc/atom/Lifeismoney.xml
"""

import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

ATOM_NS = "{http://www.w3.org/2005/Atom}"

worker_url = os.getenv("WORKER_URL")


class PTTCrawler:
    def __init__(self, board_name: str = "Lifeismoney"):
        self.feed_url = f"{worker_url}/{board_name}"

    def crawl_board(self) -> List[Dict]:
        """Fetch and parse the Atom feed for the board"""
        response = httpx.get(self.feed_url, timeout=20.0)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        articles = []

        for entry in root.findall(f"{ATOM_NS}entry"):
            title = entry.findtext(f"{ATOM_NS}title", "N/A")
            link_el = entry.find(f"{ATOM_NS}link[@rel='alternate']")
            link = link_el.get("href") if link_el is not None else None
            author_el = entry.find(f"{ATOM_NS}author/{ATOM_NS}name")
            author = author_el.text if author_el is not None else "N/A"
            published = entry.findtext(f"{ATOM_NS}published", "")

            articles.append({
                "title": title,
                "link": link,
                "author": author,
                "published": published,
            })

        return articles


def format_articles(articles: List[Dict]) -> str:
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    today = now.date()
    yesterday = today - timedelta(days=1)

    filter_keywords = ['[集中]', '[公告]', '[協尋]', '[轉錄]', '[刪除]']

    filtered = []
    for article in articles:
        if not article["link"]:
            continue

        if article["published"]:
            pub_date = datetime.fromisoformat(article["published"]).date()
            if pub_date != today and pub_date != yesterday:
                continue

        if any(kw in article["title"] for kw in filter_keywords):
            continue

        filtered.append(article)

    filtered.sort(key=lambda a: a["published"], reverse=True)

    lines = []
    for article in filtered:
        lines.append(f"{article['title']}\n{article['link']}")

    return "\n\n".join(lines)
