"""
One-time script to send VCF and welcome emails for people already uploaded to Google Sheets.
Pulls new records directly from EFAMILY MAIN Sheet2 after the known last email.
"""
import gspread
import pandas as pd
import yagmail
from google.oauth2.service_account import Credentials
from vcard_converter import create_phone_xlsx_and_vcf
from welcome_email import send_welcome_emails

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
DEST_SHEET    = "EFAMILY MAIN_20-10-25"
AFTER_EMAIL   = "brigittekande6@gmail.com"
OUTPUT_FILE   = "newcomers_final.xlsx"
HEADERS       = ["Email Address", "Name", "City", "Phone Number", "Country", "Continent"]

# Pull new records from Google Sheet
print("Connecting to Google Sheets...")
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)
sheet = gc.open(DEST_SHEET).get_worksheet(1)
all_rows = sheet.get_all_values()

# Find rows after AFTER_EMAIL
start = None
for i, row in enumerate(all_rows):
    if row[0] == AFTER_EMAIL:
        start = i + 1
        break

if start is None or start >= len(all_rows):
    print(f"No new records found after {AFTER_EMAIL}")
    exit(0)

new_rows = all_rows[start:]
print(f"Found {len(new_rows)} new records")

# Save to newcomers_final.xlsx
df = pd.DataFrame(new_rows, columns=HEADERS)
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Saved {OUTPUT_FILE}")

# Generate VCF and send to efamcare
print("\n📇 Generating VCF...")
create_phone_xlsx_and_vcf()

yag = yagmail.SMTP(user="efamcare@gmail.com", password="evkzzjrlkbepxqsm")

print("\n📨 Sending VCF to efamcare@gmail.com...")
yag.send(
    to="efamcare@gmail.com",
    subject="New Newcomers Contact List",
    contents=["Please find the new newcomers VCF attached.", "newcomers.vcf"]
)
print("✅ VCF sent!")

print("\n📨 Sending newcomers list to avation2k14@gmail.com...")
yag.send(
    to="avation2k14@gmail.com",
    subject="New Newcomers List",
    contents=["Please find the new newcomers list attached.", OUTPUT_FILE]
)
print("✅ Newcomers list sent!")

print("\n📨 Sending welcome emails...")
send_welcome_emails(OUTPUT_FILE)
print("✅ Welcome emails sent!")
