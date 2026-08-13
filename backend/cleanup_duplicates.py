import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase.json')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
            sys.exit(1)

initialize_firebase()

def cleanup():
    print("Scanning for duplicate leads...")
    db = firestore.client()
    leads_ref = db.collection('leads')
    docs = leads_ref.stream()

    seen_signatures = set()
    duplicates_deleted = 0

    for doc in docs:
        data = doc.to_dict()
        campaign_id = data.get("campaign_id", "")
        company_name = data.get("company_name", "")
        
        # We identify uniqueness by campaign + company name
        signature = f"{campaign_id}_{company_name}"
        
        if signature in seen_signatures:
            print(f"Deleting duplicate lead: {company_name} (Doc ID: {doc.id})")
            db.collection('leads').document(doc.id).delete()
            duplicates_deleted += 1
        else:
            seen_signatures.add(signature)

    print(f"\nCleanup complete! Deleted {duplicates_deleted} duplicate leads.")

if __name__ == "__main__":
    cleanup()
