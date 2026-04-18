from extractor import fetch_html, extract_text_blocks
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_client(client):
    url = client.get("link", "")

    if not url or url == "#":
        return {
            "summary": f"{client.get('title', 'This company')} is a potential B2B client.",
            "pain_points": ["Digital transformation needs", "Automation opportunities", "Scalability challenges"]
        }

    try:
        html = fetch_html(url)
        text = extract_text_blocks(html)
    except Exception as e:
        print(f"⚠️ Could not fetch {url}: {e}")
        return {
            "summary": "Unable to fetch site.",
            "pain_points": ["Unknown pain points"]
        }

    if not text or len(text.strip()) < 100:
        return {
            "summary": f"{client.get('title', 'This company')} — limited web content available.",
            "pain_points": ["Needs digital presence improvement"]
        }

    prompt = f"""
You are a B2B marketing analyst.
Summarize this company's offering in 3 concise sentences.
Then list 3 possible business challenges or pain points they might face.

Website text:
{text[:3000]}

Return ONLY this exact format:
Summary: <3 sentences>
Pain Points:
- <point 1>
- <point 2>
- <point 3>
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Groq summarizer failed: {e}")
        return {
            "summary": f"{client.get('title', 'Client')} — AI summary unavailable.",
            "pain_points": ["Could not analyze at this time"]
        }