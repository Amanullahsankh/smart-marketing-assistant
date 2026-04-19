import logging
import os
import re
import time
import requests
from dotenv import load_dotenv
from groq import Groq

logger = logging.getLogger(__name__)
load_dotenv()
ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

FAILURE_PHRASES = [
    "could not extract",
    "unable to extract",
    "not extract",
    "failed to extract",
    "no meaningful",
    "could not access"
]

def is_valid_services(text: str) -> bool:
    text_lower = text.lower()
    return not any(phrase in text_lower for phrase in FAILURE_PHRASES)


def extract_keywords(services_text):
    text = re.sub(r"[*•\-:]+", " ", services_text)
    words = re.findall(r"\b[A-Za-z]{4,}\b", text)
    ignore = {
        "solution", "service", "services", "company", "business",
        "management", "development", "platform", "provide", "helping",
        "their", "that", "with", "from", "this", "have", "will", "been"
    }
    keywords = [w.lower() for w in words if w.lower() not in ignore]
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
        if len(unique) >= 5:
            break
    return unique


def find_companies_serpapi(keyword):
    try:
        url = "https://serpapi.com/search.json"
        query = f"top companies using {keyword} solutions OR {keyword} technology"
        params = {"q": query, "api_key": SERPAPI_KEY, "num": 10}
        resp = requests.get(url, params=params, timeout=20)
        data = resp.json()
        results = data.get("organic_results", [])
        leads = []
        for r in results:
            title = r.get("title", "")
            link = r.get("link", "")
            if "job" not in title.lower() and "career" not in title.lower() and link:
                leads.append({"title": title.strip(), "link": link.strip()})
        return leads[:5]
    except Exception as e:
        logger.warning("SerpAPI request failed for %s: %s", keyword, e)
        return []


def find_companies_gemini(services_text):
    prompt = f"""
You are a B2B analyst. Given the following company services, 
list exactly 10 real-world companies that would likely need these services.
Only include actual company names, no job listings or ads.

Services:
{services_text}

Return ONLY this format (one per line):
- Company Name: one line reason
"""
    try:
        response = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("AI discovery request failed: %s", e)
        return ""


def discover_clients(services_text):
    logger.info("Discovering clients for given services.")
    if not is_valid_services(services_text):
        logger.warning("Invalid services text. Stopping discovery.")
        return []

    keywords = extract_keywords(services_text)
    logger.info("Extracted keywords: %s", keywords)

    all_leads = []

    if SERPAPI_KEY and keywords:
        for kw in keywords:
            leads = find_companies_serpapi(kw)
            all_leads.extend(leads)
            time.sleep(1)

    if not all_leads:
        logger.info("SerpAPI unavailable; falling back to AI discovery.")
        ai_output = find_companies_gemini(services_text)
        for line in ai_output.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                parts = line.replace("- ", "").split(":", 1)
                if len(parts) == 2:
                    all_leads.append({
                        "title": parts[0].strip(),
                        "link": "#",
                        "reason": parts[1].strip()
                    })
                elif parts[0].strip():
                    all_leads.append({
                        "title": parts[0].strip(),
                        "link": "#",
                        "reason": ""
                    })

    seen = set()
    unique_leads = []
    for lead in all_leads:
        title = lead.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            unique_leads.append(lead)

    logger.info("Found %d potential leads.", len(unique_leads))
    return unique_leads[:10]


if __name__ == "__main__":
    test = """
    - Game Development: Full-cycle 2D & 3D game development.
    - AR/VR Solutions: Immersive virtual reality experiences.
    - Metaverse Development: Custom metaverse environments.
    """
    leads = discover_clients(test)
    for l in leads:
        logger.info("%s -> %s", l['title'], l.get('link', '#'))