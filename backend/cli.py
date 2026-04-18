import os
import requests
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# 🧩 1️⃣ Extract Clean Keywords
# -----------------------------
def extract_keywords(services_text):
    """Extract core industry keywords from extracted services."""
    text = re.sub(r"[*•\-:]+", " ", services_text)
    words = re.findall(r"\b[A-Za-z]{3,}\b", text)
    ignore = {"solution", "service", "services", "company", "business", "management"}
    keywords = [w.lower() for w in words if w.lower() not in ignore]
    return list(set(keywords))[:5]


# -----------------------------
# 🔍 2️⃣ Use SerpAPI (Smarter Query)
# -----------------------------
def find_companies_serpapi(keyword):
    """Find companies likely to need these services."""
    try:
        url = "https://serpapi.com/search.json"
        query = f"top companies using {keyword} technology OR {keyword} solutions OR {keyword} platform"
        params = {"q": query, "api_key": SERPAPI_KEY, "num": 10}

        resp = requests.get(url, params=params, timeout=10)
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
        print(f"⚠️ SerpAPI failed for {keyword}: {e}")
        return []


# -----------------------------
# 🤖 3️⃣ OpenAI Fallback
# -----------------------------
def find_companies_openai(services_text):
    """Ask OpenAI to name real companies that might need these services."""
    prompt = f"""
You are a B2B analyst. Given the following company services, list 10 real-world companies 
that would likely need or collaborate on these services. Include only actual companies, 
not job listings or ads.

Services:
{services_text}

Return in this format:
- Company Name: reason (1 line)
"""
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI discovery failed: {e}")
        return "⚠️ Could not fetch potential clients."


# -----------------------------
# 🚀 4️⃣ Main Function
# -----------------------------
def discover_clients(services_text):
    """Discover relevant B2B clients intelligently."""
    print("🔍 Discovering clients for given services...")
    keywords = extract_keywords(services_text)
    print(f"🧩 Extracted keywords: {keywords}")

    all_leads = []

    # 🌐 Try SerpAPI if available
    if SERPAPI_KEY:
        for kw in keywords:
            leads = find_companies_serpapi(kw)
            all_leads.extend(leads)

    # 🧠 If no SerpAPI or poor results, use OpenAI reasoning
    if not all_leads:
        print("⚠️ Using AI reasoning fallback for discovery.")
        ai_output = find_companies_openai(services_text)
        for line in ai_output.split("\n"):
            if line.strip().startswith("- "):
                parts = line.replace("- ", "").split(":", 1)
                if len(parts) == 2:
                    all_leads.append({"title": parts[0].strip(), "link": "#", "reason": parts[1].strip()})
                else:
                    all_leads.append({"title": parts[0].strip(), "link": "#", "reason": ""})

    # 🧹 Remove duplicates
    seen = set()
    unique_leads = []
    for lead in all_leads:
        title = lead["title"]
        if title not in seen:
            seen.add(title)
            unique_leads.append(lead)

    print(f"✅ Found {len(unique_leads)} potential leads.")
    return unique_leads[:10]


# -----------------------------
# 🧪 Test
# -----------------------------
if __name__ == "__main__":
    test_services = """
    - Game Development: Full-cycle 2D & 3D game development for mobile, PC, and consoles.
    - AR/VR Solutions: Immersive virtual reality and augmented reality experiences.
    - Metaverse Development: Custom metaverse environments and digital ecosystems.
    """
    leads = discover_clients(test_services)
    for l in leads:
        print(f"🔗 {l['title']} → {l.get('link', '#')}")
