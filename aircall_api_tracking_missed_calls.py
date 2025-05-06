# air_call_analysis.py
"""
A script to analyze missed calls from Aircall API and update Google Sheets reports.
"""

import os
import time
from datetime import datetime, timedelta
import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "Call Monitoring Dashboard"  # Replace with your sheet name
API_BASE_URL = "https://api.aircall.io/v1/"

def authenticate_google_sheets():
    """Authenticate with Google Sheets API using service account credentials."""
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.getenv("GOOGLE_CREDS_JSON")),
        SCOPES
    )
    return gspread.authorize(credentials)

def get_aircall_calls(start_timestamp):
    """Fetch call data from Aircall API."""
    headers = {
        "Authorization": f"Bearer {os.getenv('AIR_CALL_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    calls = []
    current_page = 1
    
    while True:
        url = f"{API_BASE_URL}calls?from={start_timestamp}&page={current_page}&per_page=50"
        response = requests.get(url, headers=headers)
        data = response.json()
        
        calls.extend(data.get("calls", []))
        
        if not data.get("meta", {}).get("next_page_link"):
            break
            
        current_page += 1
        time.sleep(0.5)  # Rate limiting
        
    return pd.json_normalize(calls)

def process_calls(raw_calls_df):
    """Process raw call data into analysis-ready format."""
    processed = pd.DataFrame()
    
    # Basic transformations
    processed["id"] = raw_calls_df["id"]
    processed["start_time"] = pd.to_datetime(raw_calls_df["started_at"], unit="s")
    processed["answered_time"] = pd.to_datetime(raw_calls_df["answered_at"], unit="s", errors="coerce")
    processed["missed"] = raw_calls_df["answered_at"].isna().map({True: "yes", False: "no"})
    
    # Phone number cleaning
    for col in ["to", "from"]:
        processed[col] = (
            raw_calls_df["number.digits" if col == "to" else "raw_digits"]
            .str.replace(r"[+\- ]", "", regex=True)
        )
    
    # Additional features
    processed["line"] = raw_calls_df["number.name"]
    processed["duration"] = raw_calls_df["duration"]
    processed["tags"] = raw_calls_df["tags"].apply(
        lambda x: x[0]["name"] if x else pd.NA
    )
    
    return processed

def update_google_sheet(worksheet, df):
    """Update a Google Sheet worksheet with new data."""
    worksheet.clear()
    
    # Update headers
    headers = df.columns.tolist() + ["Update Time", "Time Since Missed"]
    worksheet.update([headers], range_name="A1:L1")
    
    # Update data
    data = df.fillna("none").values.tolist()
    worksheet.update(data, range_name=f"A2:J{len(df)+1}")
    
    # Add timestamps and formulas
    now_formula = [["=TEXT(NOW(), \"YY-MM-DD HH:MM:SS\")"] for _ in df.iterrows()]
    worksheet.update(now_formula, range_name=f"K2:K{len(df)+1}")
    
    formula_col = [
        [f"=K{idx+2}-B{idx+2}"] for idx in range(len(df))
    ]
    worksheet.update(formula_col, range_name=f"L2:L{len(df)+1}")

def main():
    """Main execution flow."""
    # Authenticate services
    gc = authenticate_google_sheets()
    monitor_sheet = gc.open(SHEET_NAME)
    
    # Get call data
    start_time = int(datetime(2022, 7, 1).timestamp()  # Example date, can parameterize
    raw_calls = get_aircall_calls(start_time)
    
    # Process data
    processed_calls = process_calls(raw_calls)
    missed_calls = processed_calls.query("missed == 'yes' and direction == 'inbound'")
    
    # Categorize missed calls
    line_categories = {
        "cs_lines": lambda x: "CS" in x,
        "sales_lines": lambda x: "Sales" in x,
        # Add other categories as needed
    }
    
    # Update all relevant sheets
    sheets_mapping = {
        "missed_all": missed_calls,
        "missed_sales": missed_calls[missed_calls["line"].str.contains("Sales")],
        # Add other sheet mappings
    }
    
    for sheet_name, data in sheets_mapping.items():
        worksheet = monitor_sheet.worksheet(sheet_name)
        update_google_sheet(worksheet, data)

if __name__ == "__main__":
    main()