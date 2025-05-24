from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_article_data(article_data: dict) -> str:
    try:
        result = supabase.table("articles").insert(article_data).execute()
        if result and result.data:
            article_id = result.data[0].get('id')
            return article_id
        else:
            print("⚠️ Inget svar från databasen vid sparande av artikel")
            return None
    except Exception as e:
        print("❌ Fel vid sparande av artikel i databasen:", str(e))
        return None

def article_exists(url: str) -> bool:
    result = supabase.table("articles").select("url").eq("url", url).execute()
    return len(result.data) > 0

def load_active_feeds() -> list[dict]:
    response = supabase.table("feeds").select("id,name,url").eq("enabled", True).execute()
    if response.data:
        return [{"id": feed["id"], "name": feed["name"], "url": feed["url"]} for feed in response.data]
    return []

def get_articles_by_status(status: int) -> list[dict]:
    try:
        print(f"\n🔍 Hämtar artiklar med status {status}...")
        result = supabase.table("articles").select("*").eq("status", status).execute()
        if result and result.data:
            print(f"✅ Hittade {len(result.data)} artiklar")
            return result.data
        else:
            print("ℹ️ Inga artiklar hittades med denna status")
            return []
    except Exception as e:
        print(f"❌ Fel vid hämtning av artiklar: {str(e)}")
        return []

def get_article_by_id(article_id: str):
    try:
        result = supabase.table("articles").select("*").eq("id", article_id).execute()
        return result.data[0] if result and result.data else None
    except Exception as e:
        print(f"❌ Fel vid hämtning av artikel {article_id}:", str(e))
        return None

def update_article_data(article_id: str, update_data: dict) -> None:
    try:
        article = get_article_by_id(article_id)
        if not article:
            print(f"❌ Artikel med ID {article_id} hittades inte i databasen")
            return
            
        result = supabase.table("articles").update(update_data).eq("id", article_id).execute()
        
        if result and hasattr(result, 'data') and result.data:
            None
        else:
            print("⚠️ Varning: Inget data returnerades från uppdateringen")
    except Exception as e:
        print("❌ Fel vid uppdatering av artikel:", str(e))
        raise e

def save_keywords(article_id: str, keywords: list[str]) -> None:
    try:
        # Ta bort gamla nyckelord
        supabase.table("article_keywords").delete().eq("article_id", article_id).execute()
        
        # Lägg till nya nyckelord
        if keywords:
            keyword_data = [{"article_id": article_id, "keyword": kw} for kw in keywords]
            result = supabase.table("article_keywords").insert(keyword_data).execute()
            
            if result and result.data:
                None
            else:
                print("⚠️ Varning: Inga nyckelord sparades")
    except Exception as e:
        print("❌ Fel vid sparande av nyckelord:", str(e))
        raise e