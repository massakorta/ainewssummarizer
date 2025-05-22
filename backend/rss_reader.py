import feedparser
from typing import List
from dataclasses import dataclass
from datetime import datetime
@dataclass
class RSSEntry:
    title: str
    link: str

def fetch_rss_entries_today(rss_url):
    feed = feedparser.parse(rss_url)
    today = datetime.now().date()
    entries_today = []

    for entry in feed.entries:
        if hasattr(entry, "published_parsed"):
            published_date = datetime(*entry.published_parsed[:3]).date()
            if published_date == today:
                entries_today.append(RSSEntry(
                        title=entry.title,
                        link=entry.link
                    ))
    return entries_today 