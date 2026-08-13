import json
import logging
import os
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)


def _load_firebase_credentials():
    """Load Firebase service account credentials from Vercel env var or local file."""
    env_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if env_json:
        try:
            parsed = json.loads(env_json)
            if isinstance(parsed, dict) and parsed.get("type") == "service_account":
                return parsed
            logger.error("FIREBASE_CREDENTIALS_JSON is present but does not contain a valid service account payload.")
            return None
        except json.JSONDecodeError:
            logger.error("FIREBASE_CREDENTIALS_JSON is present but is not valid JSON.")
            return None

    cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase.json')
    if os.path.exists(cred_path):
        return cred_path

    logger.error("Firebase credentials missing. Set FIREBASE_CREDENTIALS_JSON or provide the local firebase.json file.")
    return None


# Initialize Firebase app only once and reuse any existing default app.
def initialize_firebase():
    try:
        firebase_admin.get_app()
        logger.info("Firebase Admin already initialized; reusing the existing app.")
        return True
    except ValueError:
        pass

    try:
        cred = _load_firebase_credentials()
        if cred is None:
            raise RuntimeError("Firebase credentials are missing. Set FIREBASE_CREDENTIALS_JSON or provide the local firebase.json file.")

        firebase_admin.initialize_app(credentials.Certificate(cred))
        logger.info("Firebase Admin initialized successfully.")
        return True
    except Exception as e:
        logger.exception(f"Failed to initialize Firebase: {e}")
        raise

# Ensure initialization on import
initialize_firebase()

def save_campaign_to_firebase(data: dict) -> str:
    """
    Saves the structured campaign data and leads to Firestore.
    Returns the campaign document ID if successful, otherwise None.
    """
    try:
        initialize_firebase()
        db = firestore.client()
        
        # 1. Save Campaign Data
        campaign_data = {
            "company_input": data.get("company_url", ""),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        campaigns_ref = db.collection('campaigns')
        _, campaign_doc = campaigns_ref.add(campaign_data)
        campaign_id = campaign_doc.id
        
        # 2. Save Leads Data
        import re
        leads_ref = db.collection('campaigns').document(campaign_id).collection('leads')
        for lead in data.get("leads", []):
            title = lead.get("title", "Unknown")
            link = lead.get("link", "")
            industry = lead.get("industry", "Unknown")
            
            # Smart email generation
            domain = link.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            lead_email = f"contact@{domain}" if domain else "contact@unknown.com"
            
            # Next followup date (+2 days)
            next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)
            
            # Deterministic Document ID to prevent duplicates
            safe_company = re.sub(r'[^a-zA-Z0-9]', '', title).lower()
            if not safe_company:
                safe_company = "unknown"
            lead_doc_id = f"{campaign_id}_{safe_company}"
            
            lead_doc = {
                "lead_email": lead_email,
                "company_name": title,
                "persona": industry,
                "last_action": "Email 1 Sent",
                "next_followup_date": next_date.isoformat(),
                "status": "In Progress",
                "campaign_id": campaign_id,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            
            # Upsert: Overwrite if exists, create if it doesn't
            leads_ref.document(lead_doc_id).set(lead_doc, merge=True)
            
        logger.info(f"Successfully saved campaign {campaign_id} and leads to Firebase.")
        return campaign_id
        
    except Exception as e:
        logger.exception(f"Error saving campaign to Firebase: {e}")
        return None
