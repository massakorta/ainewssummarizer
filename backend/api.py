from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase_db import supabase

app = Flask(__name__)
CORS(app)

@app.route("/articles")
def get_articles():
    try:
        # Validera och hämta query parameters
        try:
            limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 artiklar per request
            offset = max(int(request.args.get('offset', 0)), 0)   # Inte tillåta negativ offset
        except ValueError:
            return jsonify({"error": "Ogiltiga parametrar"}), 400
        
        # Hämta artiklar med status 2 (AI-processade) och deras nyckelord
        result = supabase.table("articles") \
            .select("*, article_keywords(keyword)") \
            .eq("status", 2) \
            .order("published", desc=True) \
            .limit(limit) \
            .offset(offset) \
            .execute()
            
        # Formatera om svaret för att få nyckelorden som en lista
        articles = []
        for article in result.data:
            keywords = [k["keyword"] for k in article.pop("article_keywords", [])]
            article["keywords"] = keywords
            articles.append(article)
            
        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10123))
    app.run(host="0.0.0.0", port=port)