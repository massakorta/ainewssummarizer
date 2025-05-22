import json
import os

DB_FILE = "seen_articles.json"
ARTICLES_FILE = "articles.json"

def load_seen_articles() -> set:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_articles(articles: set) -> None:
    with open(DB_FILE, 'w') as f:
        json.dump(list(articles), f)

def save_article_data(article_data: dict) -> None:
    if not os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, 'w') as f:
            json.dump([], f)
    with open(ARTICLES_FILE, 'r') as f:
        articles = json.load(f)
    articles.append(article_data)
    with open(ARTICLES_FILE, 'w') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def load_all_articles() -> list[dict]:
    if not os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, 'w') as f:
            json.dump([], f)
    with open(ARTICLES_FILE, 'r') as f:
        return json.load(f)