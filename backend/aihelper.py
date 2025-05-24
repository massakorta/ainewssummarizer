import os
from openai import OpenAI

def summarize_to_structure(text: str) -> dict:
    import json
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = f"""Sammanfatta följande spanska nyhetsartikel på svenska och returnera exakt detta JSON-objekt:

{{
  "headline": (en intressant rubrik på max 30 tecken),
  "short_summary": (ca 125 tecken lång sammanfattning),
  "long_summary": (ca 600 tecken som förklarar innehållet tydligt),
  "category": (en kategori som t.ex. 'utrikes', 'politik', 'sport', 'kultur'),
  "keywords": (en lista med 3 till 7 viktiga nyckelord)
}}

Svara endast med ett JSON-objekt och ingenting annat. Här är artikeln:\n\n{text}"""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        instructions="Du är en svensk journalist som sammanfattar nyheter på ett enkelt och strukturerat sätt.",
        input=prompt,
        max_tokens=800,
        response_format="json"
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("⚠️ Kunde inte tolka GPT-svaret som JSON:", response.choices[0].message.content)
        return {}
