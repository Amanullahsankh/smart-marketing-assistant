import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import firebase_logger

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

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    campaign_id: str = None
    company_name: str = None

@app.post("/run-campaign")
async def run_campaign(req: CampaignRequest):
    from extractor import extract_services, is_valid_service_text
    from discovery import discover_clients
    from summarizer import summarize_client
    from emailer import generate_email, filter_icp
    from portfolio import create_portfolio
    from sheets_logger import log_to_sheet
    from drive_uploader import upload_to_drive
    from firebase_logger import save_campaign_to_firebase
    import datetime

    services = extract_services(req.website_url, limit=req.page_limit)
    if not is_valid_service_text(services):
        logger.warning("Service extraction failed for %s", req.website_url)
        return {"error": "Could not extract services from this website."}

    leads = discover_clients(services)
    results = []
    for client in leads:
        try:
            summary = summarize_client(client)
            
            # Step 1: ICP Filtering
            is_match = filter_icp(services, summary)
            if not is_match:
                logger.info(f"Skipping {client.get('title')} due to ICP mismatch.")
                continue

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
    
    # Upload to Google Drive
    drive_link = upload_to_drive(pdf_path)
    final_portfolio_ref = drive_link if drive_link else os.path.basename(pdf_path)

    # Cleanup local file if successfully uploaded
    if drive_link and os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
            logger.info(f"Deleted local file {pdf_path} after successful Drive upload.")
        except Exception as e:
            logger.error(f"Failed to delete local file {pdf_path}: {e}")

    # Save to Google Sheets
    try:
        for r in results:
            r["portfolio"] = final_portfolio_ref
        log_to_sheet(results)
    except Exception:
        logger.exception("Sheet logging failed.")

    # Save to Firebase Firestore
    firebase_doc_id = None
    try:
        # Structure the data as requested
        final_data = {
            "company_url": req.website_url,
            "extracted_services": services,
            "leads": leads,
            "summaries": [r["summary"] for r in results],
            "emails": [r["email"] for r in results],
            "portfolio_link": final_portfolio_ref,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        firebase_doc_id = save_campaign_to_firebase(final_data)
    except Exception:
        logger.exception("Firebase logging failed.")

    return {
        "services": services,
        "leads": leads,
        "results": results,
        "portfolio": final_portfolio_ref,
        "firebase_doc_id": firebase_doc_id
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/send-email")
async def send_email_api(req: EmailRequest):
    from email_service import send_email
    from firebase_admin import firestore
    import re
    from fastapi import HTTPException
    
    try:
        # Call the email service
        send_email(req.to_email, req.subject, req.body)
        
        # Update Firebase status
        if req.campaign_id and req.company_name:
            safe_company = re.sub(r'[^a-zA-Z0-9]', '', req.company_name).lower()
            if not safe_company:
                safe_company = "unknown"
            lead_doc_id = f"{req.campaign_id}_{safe_company}"
            
            db = firestore.client()
            lead_ref = db.collection('campaigns').document(req.campaign_id).collection('leads').document(lead_doc_id)
            lead_ref.update({
                "status": "Sent",
                "last_action": "Email 1 Sent"
            })
            
        return {"status": "success", "message": "Email sent"}
    except Exception as e:
        logger.exception("Failed to send email")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns")
async def get_campaigns():
    from firebase_admin import firestore
    try:
        db = firestore.client()
        docs = db.collection('campaigns').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        campaigns = []
        for doc in docs:
            c = doc.to_dict()
            c["id"] = doc.id
            campaigns.append(c)
        return campaigns
    except Exception as e:
        logger.exception("Failed to fetch campaigns")
        return {"error": str(e)}

@app.get("/leads")
async def get_leads(campaign_id: str = None):
    from firebase_admin import firestore
    try:
        if not campaign_id:
            return []
            
        db = firestore.client()
        leads_ref = db.collection('campaigns').document(campaign_id).collection('leads')
        docs = leads_ref.order_by('created_at', direction=firestore.Query.ASCENDING).stream()
        
        leads = []
        for doc in docs:
            lead_data = doc.to_dict()
            lead_data["id"] = doc.id
            leads.append(lead_data)
            
        # Sort in memory to avoid manual composite index requirement in Firestore
        leads.sort(key=lambda x: x.get('next_followup_date', ''))
        return leads
    except Exception as e:
        logger.exception("Failed to fetch leads")
        return {"error": str(e)}

@app.get("/export-csv")
async def export_csv(campaign_id: str = None):
    from firebase_admin import firestore
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    try:
        if not campaign_id:
            return {"error": "campaign_id is required"}
            
        db = firestore.client()
        leads_ref = db.collection('campaigns').document(campaign_id).collection('leads')
        docs = leads_ref.order_by('created_at', direction=firestore.Query.ASCENDING).stream()
        
        # Sort in memory
        leads = [doc.to_dict() for doc in docs]
        leads.sort(key=lambda x: x.get('next_followup_date', ''))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Lead Email", "Company Name", "Persona", "Last Action", "Next Follow-up Date", "Status"])
        
        for data in leads:
            writer.writerow([
                data.get("lead_email", ""),
                data.get("company_name", ""),
                data.get("persona", ""),
                data.get("last_action", ""),
                data.get("next_followup_date", ""),
                data.get("status", "")
            ])
            
        output.seek(0)
        filename = f"leads_{campaign_id}.csv" if campaign_id else "leads_all.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.exception("Failed to export CSV")
        return {"error": str(e)}