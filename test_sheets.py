import gspread
from google.oauth2.service_account import Credentials
from openpyxl import Workbook
import re

# Path to your JSON credentials file
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Update this path

# Setup credentials
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Connect to Google Sheets
gc = gspread.authorize(credentials)

# Configuration
SOURCE_SHEET = "TKT_EFAMILY _FORM"
DEST_SHEET = "EFAMILY MAIN_20-10-25"

# Email validation function
def is_valid_email(email):
    if not email or len(email) < 3:
        return False
    # Strip whitespace before validation
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Name cleaning function
def clean_name(name):
    if not name:
        return name
    
    # Remove titles like Dr., Mr., Mrs., Ms., Prof., etc.
    name = re.sub(r'^(Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|Rev\.?)\s+', '', name, flags=re.IGNORECASE)
    
    # Split name into parts
    parts = name.split()
    
    # Remove single letter initials (with or without dot)
    cleaned_parts = []
    for part in parts:
        # Remove dots and check if it's a single letter
        clean_part = part.replace('.', '')
        if len(clean_part) > 1:  # Keep only parts with more than 1 character
            cleaned_parts.append(part)
    
    # Join the cleaned parts and add TKT ONLINE CAMPUS
    cleaned_name = ' '.join(cleaned_parts)
    if cleaned_name:
        cleaned_name += ' TKT ONLINE CAMPUS'
    
    return cleaned_name

try:
    # Step 1: Get last email from EFAMILY MAIN Sheet2
    print("Step 1: Getting last email from destination sheet...")
    dest_workbook = gc.open(DEST_SHEET)
    dest_sheet2 = dest_workbook.get_worksheet(1)
    dest_data = dest_sheet2.get_all_values()
    
    if len(dest_data) == 0:
        print("Destination sheet is empty!")
        exit()
    
    last_email = dest_data[-1][0]
    print(f"Last email in destination: {last_email}")
    
    # Step 2: Find that email in TKT_EFAMILY_FORM
    print("\nStep 2: Searching for email in source sheet...")
    source_workbook = gc.open(SOURCE_SHEET)
    source_sheet = source_workbook.sheet1
    source_data = source_sheet.get_all_values()
    
    # Find the row with last_email
    start_row = None
    for i, row in enumerate(source_data):
        if len(row) > 0 and row[1] == last_email:  # Email Address is column 2 (index 1)
            start_row = i + 1  # Start from next row
            print(f"Found email at row {i+1}, will copy from row {start_row+1}")
            break
    
    if start_row is None:
        print(f"Email {last_email} not found in source sheet!")
        exit()
    
    # Step 3: Get new records (skip timestamp column)
    new_records = source_data[start_row:]
    
    if len(new_records) == 0:
        print("\nNo new records to copy!")
        exit()
    
    print(f"\nStep 3: Found {len(new_records)} new records")
    
    # Step 4: Create Excel file with specific columns
    # Columns: Email Address (1), Name (2), City (3), Phone number (4)
    wb = Workbook()
    ws = wb.active
    ws.title = "Newcomers"
    
    # Add headers
    ws.append(["Email Address", "Name", "City", "Phone number  (WhatsApp Number preferred with country code) e.g.:  +91 90000 3355"])
    
    # Add new records (skip timestamp column 0, take columns 1-4)
    # Filter out invalid emails
    valid_count = 0
    invalid_count = 0
    
    for record in new_records:
        if len(record) >= 5:
            email = record[1].strip()  # Strip whitespace
            if is_valid_email(email):
                name = clean_name(record[2])  # Clean the name
                ws.append([email, name, record[3], record[4]])
                valid_count += 1
            else:
                invalid_count += 1
                print(f"Skipped invalid email: '{record[1]}'")
    
    filename = "newcomers.xlsx"
    wb.save(filename)
    print(f"\nSaved {valid_count} valid records to {filename}")
    print(f"Skipped {invalid_count} records with invalid emails")
    print("Columns: Email Address, Name, City, Phone number")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure to:")
    print("1. Put your JSON file in the same directory as this script")
    print("2. Update SHEET_NAME with your actual sheet name")
    print("3. Share your sheet with:", credentials.service_account_email if 'credentials' in locals() else "the service account email")