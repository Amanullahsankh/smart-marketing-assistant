import json
import logging
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Need broader scope to edit permissions
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_google_credentials():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")

    if creds_path and os.path.exists(creds_path):
        return Credentials.from_service_account_file(creds_path, scopes=SCOPES)

    if creds_json:
        try:
            creds_info = json.loads(creds_json)
            return Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid GOOGLE_SHEETS_CREDENTIALS_JSON: {exc}")

    logger.error("No valid Google service account credentials found in GOOGLE_SHEETS_CREDENTIALS or GOOGLE_SHEETS_CREDENTIALS_JSON.")
    return None


def upload_to_drive(file_path, folder_id=None):
    """Uploads a file to Google Drive via Service Account and makes it public."""
    # Use environment variable if not passed directly
    if not folder_id:
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

    creds = _get_google_credentials()
    if creds is None:
        return None

    try:
        service = build("drive", "v3", credentials=creds)

        metadata = {"name": os.path.basename(file_path)}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True, mimetype="application/pdf")
        
        # 1. Upload the file
        uploaded = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, webViewLink"
        ).execute()

        file_id = uploaded.get("id")
        web_view_link = uploaded.get("webViewLink")

        logger.info(f"Uploaded {metadata['name']} to Drive. File ID: {file_id}")

        # 2. Make the file publicly accessible (anyone with the link can view)
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields="id"
        ).execute()

        logger.info(f"File {file_id} is now publicly accessible via: {web_view_link}")
        return web_view_link

    except HttpError as e:
        if "storageQuotaExceeded" in str(e):
            logger.error("Service Account storage quota exceeded. Please create a folder in your personal Google Drive, share it with the service account email as Editor, and set GOOGLE_DRIVE_FOLDER_ID in .env.")
        else:
            logger.error(f"Google Drive API HttpError during upload: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Google Drive upload: {e}")
        return None
