import logging
from extractor import fetch_html, extract_text_blocks
from ai_utils import generate_ai_response
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
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
    except Exception:
        logger.exception("Could not fetch %s", url)
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
{text[:2000]}

Return ONLY this exact format:
Summary: <3 sentences>
Pain Points:
- <point 1>
- <point 2>
- <point 3>
"""
    try:
        content = generate_ai_response(
            prompt=prompt,
            model="llama-3.1-8b-instant",
            max_tokens=250,
            temperature=0.3,
            system_prompt="You are a B2B marketing analyst."
        )
        return content
    except Exception:
        logger.exception("AI summarization failed for %s", url)
        return {
            "summary": f"{client.get('title', 'Client')} — AI summary unavailable.",
            "pain_points": ["Could not analyze at this time"]
        }