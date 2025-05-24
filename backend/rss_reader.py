import feedparser
from typing import List
from dataclasses import dataclass
from datetime import datetime, UTC

@dataclass
class RSSEntry:
    title: str
    link: str
    published: datetime | None

def get_entry_date(entry) -> datetime | None:
    """Extrahera publiceringsdatum från en RSS-post"""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=UTC)
    elif hasattr(entry, "pubDate_parsed") and entry.pubDate_parsed:
        return datetime(*entry.pubDate_parsed[:6], tzinfo=UTC)
    return None

def fetch_rss_entries_today(rss_url):
    feed = feedparser.parse(rss_url)
    today = datetime.now(UTC).date()
    entries_today = []

    for entry in feed.entries:
        published = get_entry_date(entry)
        if published and published.date() == today:
            entries_today.append(RSSEntry(
                title=entry.title,
                link=entry.link,
                published=published
            ))
    return entries_today 