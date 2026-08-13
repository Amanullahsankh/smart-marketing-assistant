import logging
import os
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# Initialize Firebase app only once
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase.json')
            if not os.path.exists(cred_path):
                logger.error(f"Firebase credentials not found at {cred_path}")
                return False
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized successfully.")
            return True
        except Exception as e:
            logger.exception(f"Failed to initialize Firebase: {e}")
            return False
    return True

# Ensure initialization on import
initialize_firebase()

def save_campaign_to_firebase(data: dict) -> str:
    """
    Saves the structured campaign data and leads to Firestore.
    Returns the campaign document ID if successful, otherwise None.
    """
    if not firebase_admin._apps:
        logger.error("Cannot save to Firebase: Firebase is not initialized.")
        return None

    try:
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
