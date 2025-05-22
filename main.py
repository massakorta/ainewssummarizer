from dotenv import load_dotenv
load_dotenv()
import requests
from bs4 import BeautifulSoup
import os

from rss_reader import fetch_rss_entries_today
from aihelper import summarize_article, translate_to_swedish, shorten_the_summary
from database import load_seen_articles, save_seen_articles, save_article_data

rss_url = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
seen_articles = load_seen_articles()
new_seen_articles = set(seen_articles)

print("🔍 Hämtar dagens nyheter...\n")
entries = fetch_rss_entries_today(rss_url)

for entry in entries:
    if entry.link in seen_articles:
        print(f"⏩ Hoppar över redan sammanfattad artikel: {entry.title}")
        continue

    print(f"📰 Titel: {entry.title}")
    print(f"🔗 Länk: {entry.link}\n")
    print("🌐 Hämtar artikelinnehåll...")
    response = requests.get(entry.link)
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    article_text = "\n".join(p.get_text() for p in paragraphs)

    print("💬 Skickar till GPT...\n")
    swedish_title = translate_to_swedish(entry.title)
    summary = summarize_article(article_text)
    short_summary = shorten_the_summary(summary)

    print("📋 Rubrik:\n")
    print(swedish_title)
    print("📋 Kort sammanfattning:\n")
    print(short_summary)
    print("📋 Sammanfattning:\n")
    print(summary)
    print("\n" + "="*50 + "\n")
    
    # Save article data
    article_data = {
        "orignal_title": entry.title,
        "swedish_title": swedish_title,
        "source": "El País",
        "url": entry.link,
        "short_summary": short_summary,
        "full_summary": summary,
        "date": soup.find("time").get("datetime") if soup.find("time") else None
    }
    save_article_data(article_data)
    new_seen_articles.add(entry.link)

save_seen_articles(new_seen_articles)