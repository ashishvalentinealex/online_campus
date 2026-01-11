import gspread
from google.oauth2.service_account import Credentials
import sqlite3
from openpyxl import Workbook
from datetime import datetime

# Configuration
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
DB_FILE = 'sync_tracker.db'
SOURCE_SHEET = "TKT_EFAMILY _FORM"
DEST_SHEET = "EFAMILY MAIN_20-10-25"

# Setup database
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

def get_last_email(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT last_email FROM last_sync ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    return result[0] if result else None

def save_last_email(conn, email):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO last_sync (last_email) VALUES (?)', (email,))
    conn.commit()

# Main sync logic
def sync_sheets():
    # Connect to database
    conn = init_db()
    
    # Connect to Google Sheets
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    
    # Open destination sheet and get last email
    dest_workbook = gc.open(DEST_SHEET)
    dest_sheet = dest_workbook.get_worksheet(1)  # Sheet2
    dest_data = dest_sheet.get_all_values()
    
    if len(dest_data) > 0:
        current_last_email = dest_data[-1][0]  # Email is in first column
        print(f"Current last email in destination: {current_last_email}")
    else:
        current_last_email = None
        print("Destination sheet is empty")
    
    # Get stored last email from database
    stored_last_email = get_last_email(conn)
    print(f"Stored last email from previous run: {stored_last_email}")
    
    # Open source sheet
    source_workbook = gc.open(SOURCE_SHEET)
    source_sheet = source_workbook.sheet1
    source_data = source_sheet.get_all_values()
    
    print(f"Total records in source: {len(source_data)}")
    
    # Find the position of stored email in source sheet
    start_index = 0
    if stored_last_email:
        for i, row in enumerate(source_data):
            if row[0] == stored_last_email:
                start_index = i + 1  # Start from next record
                print(f"Found last synced email at row {i+1}")
                break
    
    # Get new records to copy
    new_records = source_data[start_index:]
    
    if len(new_records) > 0:
        print(f"Found {len(new_records)} new records to copy")
        
        # Append new records to destination
        dest_sheet.append_rows(new_records)
        print(f"Copied {len(new_records)} records to destination")
        
        # Save new records to Excel file
        wb = Workbook()
        ws = wb.active
        ws.title = "Newcomers"
        
        # Add headers if available
        if len(source_data) > 0:
            ws.append(source_data[0])  # Assuming first row is header
        
        # Add new records
        for record in new_records:
            ws.append(record)
        
        filename = f"newcomers.xlsx"
        wb.save(filename)
        print(f"Saved {len(new_records)} new records to {filename}")
        
        # Save the new last email
        new_last_email = new_records[-1][0]
        save_last_email(conn, new_last_email)
        print(f"Saved new last email: {new_last_email}")
    else:
        print("No new records to copy")
    
    conn.close()

if __name__ == "__main__":
    try:
        sync_sheets()
    except Exception as e:
        print(f"Error: {e}")
