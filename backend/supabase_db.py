from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_article_data(article_data: dict) -> None:
    # Formatera datum rätt om det finns
    if article_data.get("date"):
        dt = article_data["date"]
        if isinstance(dt, str) and "T" in dt:
            dt = datetime.fromisoformat(dt.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
            article_data["date"] = dt

    result = supabase.table("articles").insert(article_data).execute()
    if not result.data:
        print("⚠️ Inget sparades i Supabase:", result)
    else:
        print("✅ Artikel sparad i Supabase.")

def article_exists(url: str) -> bool:
    result = supabase.table("articles").select("url").eq("url", url).execute()
    return len(result.data) > 0