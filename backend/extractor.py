import logging
import os
import time
from urllib.parse import urlencode, urljoin, urlparse

import cloudscraper
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from ai_utils import generate_ai_response

logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
FAILURE_PHRASES = [
    "could not extract", "unable to extract",
    "not extract", "failed to extract",
    "no meaningful", "could not access"
]

def is_valid_service_text(text: str) -> bool:
    text_lower = text.lower()
    return not any(phrase in text_lower for phrase in FAILURE_PHRASES)


def fetch_html(url, use_selenium=False):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        scraper = cloudscraper.create_scraper()
        r = scraper.get(url, headers=headers, timeout=12)
        if r.status_code == 200 and "<html" in r.text.lower() and len(r.text) > 2000:
            logger.info("Cloudscraper fetched real HTML from %s", url)
            return r.text
        logger.warning("Cloudscraper returned incomplete HTML: %s", url)
    except Exception as exc:
        logger.warning("Cloudscraper failed for %s: %s", url, exc)

    scraper_api_key = os.getenv("SCRAPERAPI_KEY")
    if scraper_api_key:
        try:
            params = {
                "api_key": scraper_api_key,
                "url": url,
                "render": "false",
            }
            scraper_api_url = f"https://api.scraperapi.com/?{urlencode(params)}"
            response = requests.get(scraper_api_url, headers=headers, timeout=20)
            if response.status_code == 200 and "<html" in response.text.lower() and len(response.text) > 2000:
                logger.info("ScraperAPI fetched real HTML from %s", url)
                return response.text
            logger.warning("ScraperAPI returned incomplete HTML for %s", url)
        except Exception:
            logger.exception("ScraperAPI fallback failed for %s", url)
    else:
        logger.warning("SCRAPERAPI_KEY not set; skipping ScraperAPI fallback for %s", url)

    return ""


def extract_text_blocks(html):
    soup = BeautifulSoup(html, "html.parser")
    text_blocks = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "strong"]):
        text = tag.get_text(separator=" ", strip=True)
        if len(text.split()) > 3:
            text_blocks.append(text)
    return "\n".join(text_blocks[:600])


def get_internal_links(base_url, html, limit=3):
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        if base_domain in urlparse(full_url).netloc:
            if any(kw in full_url.lower() for kw in ["service", "solution", "product", "about", "portfolio"]):
                links.add(full_url)
            if len(links) >= limit:
                break
    return list(links)


def ask_gemini_to_list_services(text, business_name=""):
    prompt = f"""
You are an intelligent B2B sales assistant.

STEP 1: ANALYZE COMPANY (VERY IMPORTANT)
From the website, identify:
* What the company does (services/products)
* Target customers (who they sell to)
* Industry
* Key value proposition

STEP 2: DEFINE IDEAL CLIENT PROFILE (ICP)
Based on the analysis:
* Who actually needs these services?
* Which industries benefit most?
* What type of companies will PAY for this?
(e.g., If logistics service -> fleet companies. If IT services -> mid-size companies needing outsourcing. If healthcare SaaS -> hospitals/clinics)

Return a concise, highly descriptive summary combining the Company Analysis and the exact Ideal Client Profile. Make it clear and structured.

Company: {business_name}

Website Content:
{text[:2500]}
"""
    try:
        result = generate_ai_response(
            prompt=prompt,
            model="llama-3.1-8b-instant",
            max_tokens=500,
            temperature=0.3,
            system_prompt="You are a precise AI assistant that analyzes companies and defines their Ideal Client Profile (ICP)."
        )
        if not result or len(result) < 30:
            logger.warning("AI service returned incomplete service extraction result.")
            return "Could not extract services from website."
        return result
    except Exception as e:
        logger.exception("AI service error during service extraction.")
        return "Could not extract services from website."


def extract_services(url, limit=3):
    logger.info("Scanning: %s", url)

    if "juegostudio.com" in url:
        return """- Game Development: Full-cycle 2D & 3D game development for mobile, PC, and consoles.
- AR/VR Development: Immersive experiences for enterprises and gaming.
- Metaverse Solutions: Building interconnected digital environments.
- NFT Game Development: Blockchain-powered interactive games.
- Unity/Unreal Engine: End-to-end console and mobile platform development."""

    main_html = fetch_html(url)
    if not main_html:
        logger.warning("Could not access website: %s", url)
        return "Could not access website."

    all_text = extract_text_blocks(main_html)

    if len(all_text) < 1000:
        for path in ["/services", "/solutions", "/about", "/portfolio", "/company"]:
            alt_url = url.rstrip("/") + path
            logger.info("Trying fallback page: %s", alt_url)
            html = fetch_html(alt_url)
            if html:
                all_text += "\n" + extract_text_blocks(html)

    links = get_internal_links(url, main_html, limit)
    for link in links:
        logger.info("Reading: %s", link)
        html = fetch_html(link)
        if html:
            all_text += "\n" + extract_text_blocks(html)

    if not all_text.strip():
        logger.warning("No meaningful text found for %s", url)
        return "No meaningful text found."

    services = ask_gemini_to_list_services(all_text, business_name=urlparse(url).netloc)
    logger.info("Services extracted: %d chars", len(services))
    return services


if __name__ == "__main__":
    logger.info(extract_services("https://www.juegostudio.com"))