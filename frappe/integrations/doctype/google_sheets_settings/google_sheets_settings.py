import frappe
from frappe import _
from urllib.parse import quote
from frappe.integrations.google_oauth import GoogleOAuth
from googleapiclient.errors import HttpError
from datetime import datetime

from frappe.model.document import Document

class GoogleSheetsSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        authorization_code: DF.Password | None
        enable: DF.Check
        refresh_token: DF.Password | None
        sheet_name: DF.Data | None
        spreadsheet_id: DF.Data | None
    # end: auto-generated types

    def validate(self):
        if not frappe.db.get_single_value("Google Settings", "enable"):
            frappe.throw(_("Enable Google API in Google Settings."))

    def get_access_token(self):
        if not self.refresh_token:
            button_label = frappe.bold(_("Allow Google Sheets Access"))
            raise frappe.ValidationError(_("Click on {0} to generate Refresh Token.").format(button_label))

        oauth_obj = GoogleOAuth("sheets")
        r = oauth_obj.refresh_access_token(
            self.get_password(fieldname="refresh_token", raise_exception=False)
        )
        return r.get("access_token")

@frappe.whitelist(methods=["POST"])
def authorize_access(reauthorize=False, code=None):
    """
    If no Authorization code get it from Google and then request for Refresh Token.
    """
    try:
        account = frappe.get_single("Google Sheets Settings")
        account.check_permission("write")
        oauth_code = code or account.get_password("authorization_code", raise_exception=False)
        oauth_obj = GoogleOAuth("sheets")

        if not oauth_code or reauthorize:
            return oauth_obj.get_authentication_url(
                {
                    "redirect": f"/app/Form/{quote('Google Sheets Settings')}",
                }
            )

        r = oauth_obj.authorize(oauth_code)

        if not r.get("refresh_token"):
            frappe.log_error("No refresh token received")
            frappe.throw(_("Failed to obtain refresh token from Google."))
        account.authorization_code = oauth_code
        account.refresh_token = r.get("refresh_token")
        account.save()
        frappe.db.commit()
        frappe.msgprint(_("Google Sheets authorized successfully."))
    except Exception as e:
        frappe.log_error(f"Authorize Access Error: {str(e)}")
        frappe.throw(_("Authorization failed: {0}").format(str(e)))


def get_google_sheets_object():
    """
    Returns an object of Google Sheets.
    """
    account = frappe.get_single("Google Sheets Settings")
    oauth_obj = GoogleOAuth("sheets")

    google_sheets = oauth_obj.get_google_service_object(
        account.get_access_token(),
        account.get_password(fieldname="refresh_token", raise_exception=False)
    )
    return google_sheets, account

@frappe.whitelist()
def append_to_google_sheet(doc, method=None):
    """
    Append a new row to Google Sheet when a Job doctype record is created, populating only 'portal' columns.
    """
    account = frappe.get_single("Google Sheets Settings")
    if not account.enable:
        return

    if not (account.spreadsheet_id and account.sheet_name):
        frappe.throw(_("Spreadsheet ID or Sheet Name missing in Google Sheets Settings."))

    google_sheets, account = get_google_sheets_object()
    sheet = google_sheets.spreadsheets()

    # Initialize a row with 17 empty columns (matching Google Sheet structure)
    row = [""] * 17
    if doc.creation:
        if isinstance(doc.creation, str):
            try:
                # Try parsing string to datetime
                creation_date = datetime.strptime(doc.creation, "%Y-%m-%d %H:%M:%S.%f")
                row[0] = creation_date.strftime("%m-%d-%Y")
            except ValueError:
                # If parsing fails, use the string as-is or set empty
                row[0] = doc.creation[:10] if len(doc.creation) >= 10 else ""
        else:
            # Assume datetime
            row[0] = doc.creation.strftime("%m-%d-%Y")
    else:
        row[0] = ""  # Date

    row[1] = doc.get("type", "") if doc.get("type", "") != "TITLE 24" else f"{doc.get('type', '')}, {doc.get('title24_type', '')}"  # Job Type

    # Full Address: Concatenate customer_address, customer_city, zip_code
    row[3] = f"{doc.get('customer_address', '')}, {doc.get('customer_city', '')}, {doc.get('zip_code', '')}"  # Address

    row[4] = doc.get("company", "")  # Company
    row[10] = doc.get("job_equipment_notes", "")  # Job Description
    # print(f"Appending row: {row}")

    body = {"values": [row]}
    range_name = f"{account.sheet_name}!A1"

    try:
        result = sheet.values().append(
            spreadsheetId=account.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        frappe.msgprint(_("Row appended to Google Sheet successfully."))
    except HttpError as e:
        frappe.log_error(_("Google Sheets - Failed to append row"), str(e))
        frappe.throw(_("Google Sheets - Could not append row to Google Sheet - Error Code {0}").format(e))