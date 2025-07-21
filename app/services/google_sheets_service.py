import os
import json
from datetime import datetime
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Cấu hình logging
logger = logging.getLogger(__name__)

# Cấu hình Google Sheets
SPREADSHEET_ID = '1G-DseJjN4hZ8bL74qe-fGQt_dU4vKFYnoY1iok5KS28'
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_NAME = 'Trang tính1'

def get_sheets_service():
    """Xác thực và khởi tạo service để tương tác với Google Sheets API."""
    if not os.path.exists(CREDENTIALS_FILE):
        logger.error(f"Không tìm thấy file credentials: '{CREDENTIALS_FILE}'.")
        raise FileNotFoundError(f"Không tìm thấy file credentials: '{CREDENTIALS_FILE}'.")
    
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    return service

def write_log_to_sheet(row_data: List):
    """
    Ghi một hàng dữ liệu vào Google Sheet.
    Hàng dữ liệu cần theo định dạng: [timestamp, user_id, message]
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        body = {'values': [row_data]}
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        logger.info(f"Đã ghi vào sheet: {result}")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"Lỗi không tìm thấy file credentials khi ghi vào sheet: {e}")
    except HttpError as e:
        error_details = json.loads(e.content.decode())
        error_message = error_details.get("error", {}).get("message", "Lỗi không xác định từ Google Sheets API.")
        logger.error(f"Lỗi API Google Sheets: {error_message}")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi ghi vào sheet: {e}")
        
    return False
