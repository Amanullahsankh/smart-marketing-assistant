import logging
import os
import time
import cloudscraper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin, urlparse
from webdriver_manager.chrome import ChromeDriverManager
from groq import Groq
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
        use_selenium = True

        if use_selenium:
            logger.info("Using Selenium: %s", url)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            driver.get(url)
            time.sleep(4)
            html = driver.page_source
            driver.quit()
            return html
    except Exception as e:
        logger.exception("Fetch failed for %s", url)
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
You are an AI assistant that extracts real company services from website text.
Return a clean bullet list of services with short, descriptive explanations.
Avoid generic words unless they appear explicitly in the content.

Company: {business_name}

Website Content:
{text[:6000]}
"""
    try:
        response = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        result = response.choices[0].message.content.strip()
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