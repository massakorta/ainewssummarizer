import os
from openai import OpenAI

def summarize_to_structure(text: str) -> dict:
    import json
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = f"""Sammanfatta följande spanska nyhetsartikel på svenska och returnera exakt nedanstående JSON-objekt. 
Välj ENDAST EN av följande fördefinierade kategorier (inga andra kategorier är tillåtna):
- kultur
- politik
- hälsa
- sport
- miljö
- mode
- utbildning
- forskning
- hem, kök och trädgård
- utrikes
- ekonomi
- film
- hållbarhet
- teknik
- övrigt

Här kommer JSON formatet:

{{
  "headline": (en intressant rubrik på ca 30 tecken),
  "short_summary": (ca 125 tecken lång sammanfattning),
  "long_summary": (ca 600 tecken som förklarar innehållet tydligt),
  "category": (ENDAST EN av kategorierna listade ovan - använd exakt stavning och gemener),
  "keywords": (en lista med 1 till 7 viktiga nyckelord)
}}

Svara endast med ett JSON-objekt och ingenting annat. Här är artikeln:\n\n{text}"""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{
            "role": "system",
            "content": "Du är en svensk journalist som sammanfattar nyheter på ett enkelt och strukturerat sätt. Du är mycket noga med att ENDAST använda de fördefinierade kategorierna."
        }, {
            "role": "user",
            "content": prompt
        }],
        response_format={ "type": "json_object" }
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print("⚠️ Kunde inte tolka GPT-svaret som JSON:", response.choices[0].message.content)
        return {}
