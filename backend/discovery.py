import logging
import os
import re
import time
import requests
import json
from ai_utils import generate_ai_response
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
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
                leads.append({
                    "title": title.strip(), 
                    "link": link.strip(),
                    "industry": "Unknown",
                    "company_size": "mid-size",
                    "location": "Global",
                    "reason": "Discovered via keyword search.",
                    "relevance_score": 5
                })
        return leads[:5]
    except Exception as e:
        logger.warning("SerpAPI request failed for %s: %s", keyword, e)
        return []

GIANT_COMPANIES_BLACKLIST = {
    "walmart", "amazon", "apple", "google", "microsoft", "coca-cola", "pepsi", "pfizer",
    "facebook", "meta", "tesla", "netflix", "ibm", "cisco", "oracle", "salesforce", 
    "mcdonalds", "nike", "target", "intel", "dell", "johnson & johnson", "samsung",
    "starbucks", "disney", "toyota", "ford", "sony", "zoho", "freshworks", "tcs", "infosys",
    "wipro", "accenture", "cognizant", "capgemini", "dhl", "nubank", "jb hunt", "delhivery",
    "fedex", "ups", "maersk"
}

COMPETITOR_INDUSTRIES_BLACKLIST = [
    "saas", "software development", "it services", "product development", "software company",
    "it consultancy", "tech product", "technology provider"
]

B2C_INDUSTRIES_BLACKLIST = [
    "retail", "fashion", "hospitality", "restaurant", "food", "travel", "consumer", 
    "entertainment", "apparel", "beauty", "fitness", "ride-hailing", "b2c", "marketplace"
]

INSTITUTIONAL_BLACKLIST = [
    "hospital", "clinic", "university", "government", "state", "federal", "college", 
    "school", "institute", "ministry", "department of"
]

AMBIGUOUS_NAMES = {"gemini", "apple", "square", "block", "stripe", "uber", "ola", "zomato", "swiggy", "curefit", "gojek", "go-jek"}

def find_companies_ai(services_text):
    prompt = f"""
You are an intelligent B2B sales assistant. 
Given the following Company Analysis and Ideal Client Profile (ICP), generate exactly 10 REALISTIC companies that fit the ICP.

STEP 3: GENERATE LEADS (STRICT RULES)
Generate EXACTLY 10 companies that:
✔ Are REAL companies (must exist)
✔ Have a valid website
✔ Match the Ideal Client Profile (ICP)
✔ Are likely to BUY the service

STRICTLY AVOID:
❌ Irrelevant industries
❌ Random famous companies (e.g., Walmart, Amazon, Fortune 500 giants)
❌ Companies that don't need the service
❌ Generic or fake names

STEP 5: FINAL CHECK (THINK BEFORE GENERATING)
- Does this company actually need the service?
- Is everything realistic?
If NO -> Fix it.

Company Analysis & ICP:
{services_text}

You MUST return the output ONLY as a raw JSON array of objects. Do not wrap it in markdown code blocks.
Each object must have the exact following keys:
"title" (string): The company name.
"link" (string): A realistic website URL (e.g. https://companyname.com).
"industry" (string): The company's specific industry.
"company_size" (string): "startup", "mid-size", or "enterprise".
"location" (string): The country where the company is headquartered.
"reason" (string): Why they are a PERFECT fit and highly likely to BUY the service based on the ICP.
"relevance_score" (integer): Your confidence score from 1 to 10.
"""
    try:
        leads = generate_ai_response(
            prompt=prompt,
            model="llama-3.1-8b-instant",
            max_tokens=2500,
            temperature=0.3,
            json_mode=True,
            system_prompt="You are a precise B2B lead generation assistant that outputs strict JSON without markdown formatting."
        )
        return leads
    except Exception as e:
        logger.warning("AI discovery request failed: %s", e)
        return []

def filter_and_score_leads(leads):
    """Filters out B2C/competitors/giants/institutions and sorts by relevance."""
    filtered_leads = []
    
    for lead in leads:
        title = lead.get("title", "").strip()
        title_lower = title.lower()
        if not title:
            continue
            
        # Remove aggressive hardcoded blacklists to allow dynamic industry generation
        # We only keep the very basic ambiguous names and absolute global giants filter.
        
        # 1. Filter out giant enterprise / competitor blacklisted names
        is_giant = any(giant in title_lower or title_lower == giant for giant in GIANT_COMPANIES_BLACKLIST)
        if is_giant:
            logger.info(f"Filtered out overly large/generic/competitor company: {title}")
            continue
            
        # 2. Filter ambiguous short names
        if len(title) <= 3 or title_lower in AMBIGUOUS_NAMES:
            logger.info(f"Filtered out ambiguous name: {title}")
            continue
            
        # 3. Base AI Score
        score = lead.get("relevance_score", 5)
            
        # 4. Light Geography boost (still prefer diverse outputs if possible)
        location = lead.get("location", "").lower()
        if "india" in location:
            score += 2
        elif "usa" in location or "united states" in location:
            score += 1
            
        lead["final_score"] = score
        filtered_leads.append(lead)
        
    # Sort by final score descending
    filtered_leads.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    return filtered_leads[:10]

def discover_clients(services_text):
    logger.info("Discovering clients for given services.")
    if not is_valid_services(services_text):
        logger.warning("Invalid services text. Stopping discovery.")
        return []

    keywords = extract_keywords(services_text)
    logger.info("Extracted keywords: %s", keywords)

    all_leads = []

    # Use AI for high-quality structured leads (Main logic)
    ai_leads = find_companies_ai(services_text)
    if ai_leads and isinstance(ai_leads, list):
        all_leads.extend(ai_leads)

    # Filter, Score, and Deduplicate
    scored_leads = filter_and_score_leads(all_leads)
    
    seen = set()
    final_unique_leads = []
    for lead in scored_leads:
        title_lower = lead.get("title", "").strip().lower()
        if title_lower not in seen:
            seen.add(title_lower)
            final_unique_leads.append(lead)

    # If AI didn't return enough and SERPAPI is available, fallback logic
    if len(final_unique_leads) < 5 and SERPAPI_KEY and keywords:
        logger.info("Not enough leads generated. Falling back to SerpAPI.")
        for kw in keywords[:2]:
            serp_leads = find_companies_serpapi(kw)
            for sl in serp_leads:
                sl_title_lower = sl.get("title", "").lower()
                if sl_title_lower not in seen:
                    # Basic fallback score
                    sl["final_score"] = 5
                    final_unique_leads.append(sl)
                    seen.add(sl_title_lower)
            time.sleep(1)

    logger.info("Found %d highly relevant leads.", len(final_unique_leads))
    return final_unique_leads[:10]

if __name__ == "__main__":
    test = """
    - Custom Analytics Platforms
    - Intelligent Automation
    - Cloud Solutions
    """
    leads = discover_clients(test)
    for l in leads:
        print(f"[{l.get('final_score')}] {l['title']} ({l.get('industry')} | {l.get('company_size')} | {l.get('location')}) -> {l.get('link', '#')}")
        print(f"   Reason: {l.get('reason')}\n")