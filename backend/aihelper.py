import os
from openai import OpenAI

def summarize_article(text: str, max_length: int = 300) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du är en svensk journalist, och riktigt bra på att sammanfatta artiklar,koncist och objektivt med enkel svenska."},
            {"role": "user", "content": f"Sammanfatta följande spanska nyhetsartikel på svenska till max {max_length} tecken: \n\n{text}"}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def translate_to_swedish(text: str) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du är en översättare av text från spanska till svenska. Det ska vara så korrekt översättning som möjligt."},
            {"role": "user", "content": f"Översätt följande text till svenska. Ge endast översättningen utan förklaringar:\n\n{text}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

def shorten_the_summary(summary: str, max_length: int = 60) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Du är en svensk journalist, och riktigt bra på att sammanfatta artiklar, koncist och objektivt med enkel svenska."},
            {"role": "user", "content": f"Sammanfatta denna text till max {max_length} tecken:\n\n{summary}"}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
