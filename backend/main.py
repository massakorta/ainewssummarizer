from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import requests
from bs4 import BeautifulSoup
import os

def extract_article_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception as e:
        print(f"❌ Kunde inte extrahera text från: {url}", e)
        return ""

from rss_reader import fetch_rss_entries_today
from supabase_db import save_article_data, article_exists, load_active_feeds

feeds = load_active_feeds()

cutoff = datetime.utcnow() - timedelta(hours=24)

print("🔍 Hämtar dagens nyheter...\n")
all_entries = []
for feed in feeds:
    entries = fetch_rss_entries_today(feed["url"])
    for entry in entries:
        entry_time = entry.published_parsed if hasattr(entry, "published_parsed") else None
        if entry_time:
            published_dt = datetime(*entry_time[:6])
            if published_dt < cutoff:
                print(f"⏩ Hoppar över gammal artikel: {entry.title}")
                continue
        if article_exists(entry.link):
            print(f"⏩ Hoppar över redan sparad artikel i databasen: {entry.title}")
            continue

        print(f"📰 Titel: {entry.title}")
        print(f"🔗 Länk: {entry.link}\n")

        article_data = {
            "url": entry.link,
            "source": feed["name"],
            "published": entry.published if hasattr(entry, "published") else None,
            "status": 0,
            "feed_id": feed["id"]
        }
        save_article_data(article_data)

from supabase_db import get_articles_by_status, update_article_data, save_keywords
from aihelper import summarize_to_structure
import time

print("✍️ Bearbetar artiklar med status 0...")

articles = get_articles_by_status(0)

for article in articles:
    print(f"\n✉️ Artikel: {article['url']}")
    try:
        text = extract_article_text(article["url"])
        if not text:
            update_article_data(article["id"], {"status": -2})
            print("❌ Ingen text kunde extraheras")
            continue

        result = summarize_to_structure(text)

        update_data = {
            "swedish_title": result["headline"],
            "short_summary": result["short_summary"],
            "full_summary": result["long_summary"],
            "category": result["category"],
            "status": 2
        }

        update_article_data(article["id"], update_data)

        save_keywords(article["id"], result.get("keywords", []))

        print("✅ Klar:", result["headline"])
    except Exception as e:
        print("❌ Fel vid bearbetning:", e)
        continue

    time.sleep(1)  # undvik att träffa rate limits

# --- Analysblock för artiklar med status 2 ---
from difflib import SequenceMatcher

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

print("\n⚖ Analyserar artiklar med status 2...")

cutoff = datetime.utcnow() - timedelta(hours=24)
articles_to_check = [
    a for a in get_articles_by_status(2)
    if a.get("published") and datetime.fromisoformat(a["published"]) >= cutoff
]

for i, article in enumerate(articles_to_check):
    if not article.get("full_summary") or not article.get("swedish_title"):
        update_article_data(article["id"], {"status": -1})
        print(f"⚠️ Förkastad artikel: {article['url']}")
        continue

    found_duplicate = False
    for j, other in enumerate(articles_to_check):
        if i == j:
            continue
        if other["id"] == article["id"]:
            continue
        if other["category"] != article["category"]:
            continue
        if is_similar(article["swedish_title"], other["swedish_title"]):
            update_article_data(article["id"], {
                "status": 3,
                "duplicate_of": other["id"]
            })
            print(f"➡ Extra källa hittad: {article['swedish_title']} ⬅ {other['swedish_title']}")
            found_duplicate = True
            break

    if not found_duplicate:
        update_article_data(article["id"], {"status": 4})
        print(f"✅ Unik artikel: {article['swedish_title']}")