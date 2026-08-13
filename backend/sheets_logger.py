import json
import logging
import gspread
from gspread.exceptions import SpreadsheetNotFound, APIError
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)

load_dotenv()


def _get_service_account_credentials():
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    if creds_path and os.path.exists(creds_path):
        return ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

    if creds_json:
        try:
            creds_info = json.loads(creds_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid GOOGLE_SHEETS_CREDENTIALS_JSON: {exc}")

    logger.error("No valid Google service account credentials found in GOOGLE_SHEETS_CREDENTIALS or GOOGLE_SHEETS_CREDENTIALS_JSON.")
    return None


def init_sheet(creds_path=None, sheet_name="SmartMarketingLogs"):
    """Initialize or create a Google Sheet and return the worksheet handle."""
    creds = _get_service_account_credentials()

    if creds is None:
        if creds_path:
            logger.error(f"Credentials file not found at {creds_path}")
        else:
            logger.error("No valid Google service account credentials were available.")
        return None

    try:
        client = gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Failed to authorize Google Sheets credentials: {e}")
        return None

    # Fetch sheet ID from environment or use fallback
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "112G14ucALb0G1sK2MyI_ivB_lsAKoZy5bzg0eNWutR3g")

    try:
        sh = client.open_by_key(sheet_id)
        logger.info(f"Successfully opened Google Sheet with ID: {sheet_id}")
    except SpreadsheetNotFound:
        logger.warning(f"Spreadsheet with ID '{sheet_id}' not found. Make sure it exists and is shared with the service account email.")
        logger.info(f"Attempting to create a new sheet named '{sheet_name}'...")
        try:
            sh = client.create(sheet_name)
            logger.info(f"Successfully created new sheet: '{sheet_name}'. IMPORTANT: Share this sheet with your personal Google account to view it.")
        except APIError as e:
            if "quota" in str(e).lower() or "403" in str(e):
                logger.error("Drive storage quota exceeded or API permission denied. Cannot create a new sheet. Please free up space in the service account Drive or use an existing shared sheet.")
            else:
                logger.error(f"Google Sheets API Error during sheet creation: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating new sheet: {e}")
            return None
    except APIError as e:
        logger.error(f"Google Sheets API Error while opening sheet: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error opening sheet: {e}")
        return None

    try:
        ws = sh.sheet1
        return ws
    except Exception as e:
        logger.error(f"Error accessing the first worksheet: {e}")
        return None

def log_to_sheet(results):
    """Log campaign data to Google Sheets, with auto headers and error-safe handling."""
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")

    if not creds_path and not creds_json:
        logger.error("No Google credentials found in GOOGLE_SHEETS_CREDENTIALS or GOOGLE_SHEETS_CREDENTIALS_JSON.")
        return

    ws = init_sheet(creds_path)
    if ws is None:
        logger.error("Worksheet initialization failed. Skipping logging to Google Sheets.")
        return

    headers = [
        "Client Name",
        "Client Link",
        "Summary",
        "Email Subject",
        "Email Body",
        "Portfolio File",
        "Response Status",
        "Last Contacted"
    ]

    try:
        if not ws.get_all_values():
            ws.append_row(headers)
    except APIError as e:
        logger.error(f"API Error while reading/writing headers: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error while reading/writing headers: {e}")
        return

    for r in results:
        client = r.get("client", {})
        summary_data = r.get("summary", "")

        if isinstance(summary_data, dict):
            summary_text = summary_data.get("summary", "")
        else:
            summary_text = str(summary_data)

        email_data = r.get("email", {})
        if isinstance(email_data, dict):
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
        else:
            subject = "N/A"
            body = str(email_data)

        try:
            ws.append_row([
                client.get("title", ""),
                client.get("link", ""),
                summary_text,
                subject,
                body,
                r.get("portfolio", ""),
                "Pending",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
        except APIError as e:
            logger.error(f"API Error appending row for client '{client.get('title', 'Unknown')}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error appending row: {e}")

    logger.info("Data logging process to Google Sheets completed.")
