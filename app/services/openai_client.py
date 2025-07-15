from app.config import settings
from app.services.rag_service import search_knowledge
from litellm import acompletion
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""
Bạn là nhân viên tổng đài dí dỏm, thân thiện.
Dùng thông tin được cung cấp để trả lời chính xác, ngắn gọn.
- Tối đa {settings.max_sentences} câu, mỗi câu ≤{settings.max_tokens_per_sentence} từ.
- Giọng điệu hóm hỉnh, không sai sự thật.
"""

async def generate_reply(user_message: str) -> str:
    try:
        snippets = await search_knowledge(user_message)
        context = "\n".join(snippets)
        
        user_prompt = f"Kiến thức:\n{context}\n\nCâu hỏi: {user_message}"
        
        response = await acompletion(
            model="gemini/gemini-1.5-pro",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, 
                {"role": "user", "content": user_prompt}
            ],
            api_key=settings.gemini_api_key
        )
        
        result = response.choices[0].message.content.strip()
        logger.info(f"Generated reply for query: {user_message[:50]}...")
        return result
        
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau." 