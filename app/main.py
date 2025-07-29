from fastapi import FastAPI, Form, Request, BackgroundTasks
from app.services.openai_client import generate_reply
from app.services.smax_client import send_to_smax
from app.services.google_sheets_service import write_log_to_sheet, parse_to_sheet_row
from app.models.schemas import BookingData
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HotlineAI-RAG", version="2.0.0")

# api debug
@app.post("/webhook/smax/debug")
async def debug_smax_webhook(request: Request):
    """Debug endpoint để xem SMAX gửi gì"""
    headers = dict(request.headers)
    body = await request.body()
    
    logger.info(f"Headers: {headers}")
    logger.info(f"Body: {body}")
    logger.info(f"Content-Type: {headers.get('content-type', 'Not set')}")
    
    if headers.get('content-type') == 'application/x-www-form-urlencoded':
        form_data = await request.form()
        logger.info(f"Form data: {dict(form_data)}")
    
    return {"status": "debug_ok", "received": True}

# api chính (chatbot và ghi log lên sheet)
@app.post("/webhook/smax")
async def handle_smax_webhook(
    background_tasks: BackgroundTasks,
    message: str = Form(default=""),
    pid: str = Form(default=""),
    page_pid: str = Form(default="")
):
    logger.info(f"Received webhook: message='{message}', pid='{pid}', page_pid='{page_pid}'")
    
    # ghi log vào background
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_data = [timestamp, pid, message]
    background_tasks.add_task(write_log_to_sheet, log_data)
    
    # check if message empty
    if not message.strip():
        logger.warning(f"Empty message received from {pid}")
        return {"status": "ok", "message": "Empty message ignored"}
    
    try:
        # gen reply
        reply = await generate_reply(message)
        logger.info(f"Generated reply: {reply}")
        
        # gửi về SMAX với cả pid và page_pid
        await send_to_smax(pid, reply, page_pid)
        logger.info(f"Successfully sent reply to {pid}")
        
        return {"status": "ok", "reply": reply}
        
    except Exception as e:
        logger.error(f"Error processing message from {pid}: {str(e)}")
        return {"status": "error", "message": "Internal server error"}

@app.post("/booking/log")
async def log_booking_to_sheet(booking_data: BookingData, background_tasks: BackgroundTasks):
    """
    API endpoint để nhận thông tin booking và ghi vào Google Sheet.
    """
    try:
        # Chuyển đổi và định dạng dữ liệu
        row_data = parse_to_sheet_row(booking_data.dict())
        
        # Ghi vào sheet trong background
        background_tasks.add_task(write_log_to_sheet, row_data)
        
        logger.info(f"Đã nhận và đưa vào hàng đợi ghi sheet cho đơn: {booking_data.id_khach}")
        return {"status": "success", "message": "Đã nhận thông tin booking và đang xử lý."}
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý booking: {e}")
        return {"status": "error", "message": "Lỗi xử lý phía server."}


@app.get("/")
async def root():
    return {"message": "HotlineAI-RAG is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HotlineAI-RAG"}