import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)

load_dotenv()

def init_sheet(creds_path, sheet_name="SmartMarketingLogs"):
    """Initialize or create a Google Sheet and return the worksheet handle."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    try:
        sh = client.open(sheet_name)
    except Exception:
        sh = client.create(sheet_name)

    ws = sh.sheet1
    return ws


def log_to_sheet(results):
    """Log campaign data to Google Sheets, with auto headers and error-safe handling."""
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    ws = init_sheet(creds_path)

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

    if not ws.get_all_values():
        ws.append_row(headers)

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

    logger.info("Data successfully logged with response tracking enabled.")
