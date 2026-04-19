import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle, os

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def upload_to_drive(file_path, folder_id=None):
    """Uploads a file to your personal Google Drive via OAuth."""
    creds = None
    token_path = "user_token.pickle"
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name"
    ).execute()

    logger.info("Uploaded %s to Drive", os.path.basename(file_path))
    return uploaded.get("id")
