from flask import Flask, jsonify
from flask_cors import CORS
from supabase_db import supabase

app = Flask(__name__)
CORS(app)

@app.route("/articles")
def get_articles():
    try:
        result = supabase.table("articles").select("*").order("date", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)