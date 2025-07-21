
import os
# import re 
from datetime import datetime
import json
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Form
import uvicorn

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = FastAPI(
    title="Webhook Service",
    description="Nhận webhook từ Smax và ghi dữ liệu vào Google Sheet.",
    version="2.0.0" 
)

SPREADSHEET_ID = '1G-DseJjN4hZ8bL74qe-fGQt_dU4vKFYnoY1iok5KS28'
CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_NAME = 'Trang tính1'

# MESSAGE_REGEX = re.compile(r"đăng ký ngành (.+?) với điểm ([\d\.]+)")

def get_sheets_service():
    """Xác thực và khởi tạo service để tương tác với Google Sheets API."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Không tìm thấy file credentials: '{CREDENTIALS_FILE}'. "
                              "Vui lòng tải file JSON của service account và đặt vào thư mục dự án.")
    
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    return service


@app.post('/webhook', status_code=status.HTTP_200_OK)
async def webhook_handler(
    page_pid: str = Form(...),
    pid: str = Form(...),
    message: Optional[str] = Form(None)
):
    """
    Endpoint nhận webhook từ Smax, ghi lại toàn bộ tin nhắn của người dùng vào Google Sheet.
    """
    # Nếu không có tin nhắn (trường message rỗng hoặc không được gửi) thì bỏ qua
    if not message:
        return {"status": "no_message", "message": "Trường 'message' rỗng hoặc không được gửi."}

    print(f"Nhận được tin nhắn từ User ID {pid}: '{message}'")

    # Lấy timestamp hiện tại
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Dữ liệu hàng mới: [timestamp, user_id, message]
    new_row = [timestamp, pid, message]
    
    try:
        # Ghi vào Google Sheet
        print("Đang tiến hành ghi vào sheet...")
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        body = {
            'values': [new_row]
        }
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        print(f"Đã ghi vào sheet: {result}")
        return {"status": "success", "data_written": new_row}
        
    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except HttpError as e:
        error_details = json.loads(e.content.decode())
        error_message = error_details.get("error", {}).get("message", "Lỗi không xác định từ Google Sheets API.")
        print(f"Lỗi API Google Sheets: {error_message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi API Google Sheets: {error_message}")
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi không xác định: {str(e)}")

if __name__ == '__main__':
    uvicorn.run("webhook_app:app", host='0.0.0.0', port=8080, reload=True) 