import os
import json
from datetime import datetime
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

SPREADSHEET_ID = '1fjP12mywt8j4KcHVjmeWBTD_xmXj6TyHNnVqvyRTtR4'
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_NAME = 'chotDon'

def get_sheets_service():
    """authenticate and initialize service to interact with google sheets API"""
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

def parse_to_sheet_row(data: dict) -> List[str]:
    """
    Chuyển đổi dữ liệu từ dict sang list theo đúng thứ tự và định dạng của Google Sheet.
    Thứ tự cột: Thời gian, ID khách, Tên, SĐT, Địa chỉ đón, Địa chỉ trả, Ngày đi, Giờ xe chạy, Số lượng người, Tổng tiền.

    Args:
        data: Dictionary chứa thông tin đơn hàng từ JSON request.

    Returns:
        List các chuỗi đã được định dạng để ghi vào sheet.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Định dạng số lượng người, ví dụ: 5 -> "5 người"
    so_luong_nguoi = data.get('so_luong_nguoi')
    formatted_so_luong = f"{so_luong_nguoi} người" if so_luong_nguoi is not None else ""

    # Định dạng tổng tiền, ví dụ: 1500000 -> "1.500.000 VNĐ"
    tong_tien = data.get('tong_tien', 0)
    formatted_tong_tien = f"{int(tong_tien):,} VNĐ".replace(',', '.')

    # ánh xạ data
    row_data = [
        timestamp,
        str(data.get('id_khach', '')),
        str(data.get('ten', '')),
        str(data.get('sdt', '')),
        str(data.get('dia_chi_don', '')),
        str(data.get('dia_chi_tra', '')),
        str(data.get('ngay_di', '')),
        str(data.get('gio_xe_chay', '')),
        formatted_so_luong,
        formatted_tong_tien,
    ]

    return row_data