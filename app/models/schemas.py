# app/models/schemas.py
from pydantic import BaseModel, Field

class SmaxWebhook(BaseModel):
    """Payload webhook gửi từ Smax"""
    message: str = Field(..., description="Nội dung tin nhắn của user")
    pid: str = Field(..., description="ID người gửi trên Zalo/Smax")
    page_pid: str = Field(..., description="ID trang/page trên Smax")

class SmaxSendRequest(BaseModel):
    """Payload gửi ngược lại cho Smax"""
    sender_id: str
    message: str