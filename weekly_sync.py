"""
Complete Weekly Sync Script for Online Campus
This script performs the following steps:
1. Get last email from EFAMILY MAIN Sheet2
2. Find that email in TKT_EFAMILY_FORM and extract new records
3. Validate emails and clean names
4. Enrich data with OpenAI (country, continent, phone validation)
5. Clean phone numbers (remove spaces, +, -)
6. Upload to Google Sheets Sheet2
7. Store last email for next sync
"""

import gspread
from google.oauth2.service_account import Credentials
from openpyxl import Workbook
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3
import json
import re
import os

# Load environment variables
load_dotenv()

# Configuration
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
SOURCE_SHEET = "TKT_EFAMILY _FORM"
DEST_SHEET = "EFAMILY MAIN_20-10-25"
DB_FILE = 'sync_tracker.db'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# ============= DATABASE FUNCTIONS =============
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_sync (
            id INTEGER PRIMARY KEY,
            last_email TEXT,
            sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def save_last_email(conn, email):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO last_sync (last_email) VALUES (?)', (email,))
    conn.commit()

# ============= VALIDATION FUNCTIONS =============
def is_valid_email(email):
    if not email or len(email) < 3:
        return False
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def clean_name(name):
    if not name:
        return name
    
    # Remove titles
    name = re.sub(r'^(Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|Rev\.?)\s+', '', name, flags=re.IGNORECASE)
    
    # Split and remove single letter initials
    parts = name.split()
    cleaned_parts = []
    for part in parts:
        clean_part = part.replace('.', '')
        if len(clean_part) > 1:
            cleaned_parts.append(part)
    
    # Add TKT ONLINE CAMPUS
    cleaned_name = ' '.join(cleaned_parts)
    if cleaned_name:
        cleaned_name += ' TKT ONLINE CAMPUS'
    
    return cleaned_name

def clean_phone_number(phone):
    if not phone:
        return phone
    return re.sub(r'[^0-9]', '', str(phone))

# ============= OPENAI ENRICHMENT =============
def get_location_and_phone_info(city, phone):
    prompt = f"""Given the following information:
City: {city}
Phone: {phone}

Please provide a JSON response with:
1. country: The country name for this city
2. continent: The continent name
3. phone_corrected: The phone number with proper country code (if missing, add it based on the country)

Format the response as valid JSON only, no additional text:
{{
    "country": "country name",
    "continent": "continent name",
    "phone_corrected": "phone with country code"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides geographic and phone number information. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result, response.usage
    except Exception as e:
        print(f"  ⚠️  Error with OpenAI: {e}")
        return {
            "country": "Unknown",
            "continent": "Unknown",
            "phone_corrected": phone
        }, None

# ============= MAIN SYNC FUNCTION =============
def sync_weekly():
    print("=" * 60)
    print("ONLINE CAMPUS WEEKLY SYNC")
    print("=" * 60)
    
    # Initialize database
    conn = init_db()
    
    # Connect to Google Sheets
    print("\n[1/7] Connecting to Google Sheets...")
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    
    # Step 1: Get last email from destination
    print("[2/7] Getting last email from EFAMILY MAIN Sheet2...")
    dest_workbook = gc.open(DEST_SHEET)
    dest_sheet2 = dest_workbook.get_worksheet(1)
    dest_data = dest_sheet2.get_all_values()
    
    if len(dest_data) == 0:
        print("❌ Destination sheet is empty!")
        return
    
    last_email = dest_data[-1][0]
    print(f"      Last email: {last_email}")
    
    # Step 2: Find email in source and get new records
    print("[3/7] Searching for new records in TKT_EFAMILY_FORM...")
    source_workbook = gc.open(SOURCE_SHEET)
    source_sheet = source_workbook.sheet1
    source_data = source_sheet.get_all_values()
    
    start_row = None
    for i, row in enumerate(source_data):
        if len(row) > 0 and row[1] == last_email:
            start_row = i + 1
            break
    
    if start_row is None:
        print(f"❌ Email {last_email} not found in source sheet!")
        return
    
    new_records = source_data[start_row:]
    
    if len(new_records) == 0:
        print("✅ No new records to sync!")
        return
    
    print(f"      Found {len(new_records)} new records")
    
    # Step 3: Validate emails and clean names
    print("[4/7] Validating emails and cleaning names...")
    validated_records = []
    invalid_count = 0
    
    for record in new_records:
        if len(record) >= 5:
            email = record[1].strip()
            if is_valid_email(email):
                name = clean_name(record[2])
                validated_records.append({
                    'email': email,
                    'name': name,
                    'city': record[3],
                    'phone': record[4]
                })
            else:
                invalid_count += 1
    
    print(f"      Valid: {len(validated_records)}, Invalid: {invalid_count}")
    
    if len(validated_records) == 0:
        print("❌ No valid records to process!")
        return
    
    # Step 4: Enrich with OpenAI
    print(f"[5/7] Enriching data with OpenAI ({len(validated_records)} records)...")
    enriched_records = []
    total_tokens = 0
    
    for idx, record in enumerate(validated_records, 1):
        print(f"      [{idx}/{len(validated_records)}] {record['name'][:30]}...")
        
        info, usage = get_location_and_phone_info(record['city'], record['phone'])
        
        if usage:
            total_tokens += usage.total_tokens
        
        enriched_records.append({
            'email': record['email'],
            'name': record['name'],
            'city': record['city'],
            'phone': info['phone_corrected'],
            'country': info['country'],
            'continent': info['continent']
        })
    
    print(f"      Tokens used: {total_tokens:,}")
    
    # Step 5: Clean phone numbers
    print("[6/7] Cleaning phone numbers...")
    final_records = []
    for record in enriched_records:
        final_records.append([
            record['email'],
            record['name'],
            record['city'],
            clean_phone_number(record['phone']),
            record['country'],
            record['continent']
        ])
    
    # Step 6: Upload to Google Sheets
    print(f"[7/7] Uploading {len(final_records)} records to Google Sheets...")
    dest_sheet2.append_rows(final_records)
    
    # Save last email
    last_email_new = final_records[-1][0]
    save_last_email(conn, last_email_new)
    
    print("\n" + "=" * 60)
    print("✅ SYNC COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 Records processed: {len(final_records)}")
    print(f"📧 Last email stored: {last_email_new}")
    print(f"🤖 OpenAI tokens used: {total_tokens:,}")
    
    # Calculate cost
    input_cost = (total_tokens * 0.5 / 1_000_000) * 0.150
    output_cost = (total_tokens * 0.5 / 1_000_000) * 0.600
    total_cost = input_cost + output_cost
    print(f"💰 Estimated cost: ${total_cost:.4f}")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        exit(1)
    
    try:
        sync_weekly()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
