import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class CampaignRequest(BaseModel):
    business_name: str
    website_url: str
    page_limit: int = 2

@app.post("/run-campaign")
async def run_campaign(req: CampaignRequest):
    from extractor import extract_services, is_valid_service_text
    from discovery import discover_clients
    from summarizer import summarize_client
    from emailer import generate_email
    from portfolio import create_portfolio
    from sheets_logger import log_to_sheet

    services = extract_services(req.website_url, limit=req.page_limit)
    if not is_valid_service_text(services):
        logger.warning("Service extraction failed for %s", req.website_url)
        return {"error": "Could not extract services from this website."}

    leads = discover_clients(services)
    results = []
    for client in leads:
        try:
            summary = summarize_client(client)
            email = generate_email(
                req.business_name,
                req.website_url,
                services,
                client,
                summary
            )
            results.append({
                "client": client,
                "summary": summary if isinstance(summary, str) else str(summary),
                "email": email
            })
        except Exception:
            logger.exception("Error processing client %s", client.get("title"))

    pdf_path = create_portfolio(req.business_name, services)
    pdf_path = create_portfolio(req.business_name, services)

    try:
        for r in results:
            r["portfolio"] = os.path.basename(pdf_path)
        log_to_sheet(results)
    except Exception:
        logger.exception("Sheet logging failed.")

    return {
        "services": services,
        "leads": leads,
        "results": results,
        "portfolio": os.path.basename(pdf_path)
    }

@app.get("/health")
async def health():
    return {"status": "ok"}