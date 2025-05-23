from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase_db import supabase

app = Flask(__name__)
CORS(app)

@app.route("/articles")
def get_articles():
    try:
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        result = supabase.table("articles") \
            .select("*") \
            .order("date", desc=True) \
            .limit(limit) \
            .offset(offset) \
            .execute()
            
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10123))
    app.run(host="0.0.0.0", port=port)