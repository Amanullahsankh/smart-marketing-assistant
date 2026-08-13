import os
import logging
from firebase_admin import credentials, firestore
import firebase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def migrate_leads():
    if not initialize_firebase():
        logger.error("Could not initialize firebase")
        return
        
    db = firestore.client()
    
    # Get all documents from the flat 'leads' collection
    logger.info("Fetching flat leads...")
    leads_ref = db.collection('leads')
    docs = leads_ref.stream()
    
    count = 0
    missing_campaign_id = 0
    for doc in docs:
        lead_data = doc.to_dict()
        lead_id = doc.id
        
        campaign_id = lead_data.get('campaign_id')
        if not campaign_id:
            logger.warning(f"Lead {lead_id} is missing 'campaign_id'. Skipping.")
            missing_campaign_id += 1
            continue
            
        # Add to new subcollection: campaigns/{campaign_id}/leads/{lead_id}
        subcoll_ref = db.collection('campaigns').document(campaign_id).collection('leads').document(lead_id)
        
        # Set the data (merge=True just in case)
        subcoll_ref.set(lead_data, merge=True)
        count += 1
        
        logger.info(f"Migrated lead {lead_id} into campaign {campaign_id}")
        
    logger.info(f"Migration complete! Successfully copied {count} leads.")
    if missing_campaign_id > 0:
        logger.warning(f"Skipped {missing_campaign_id} leads due to missing campaign_id.")

if __name__ == "__main__":
    migrate_leads()
