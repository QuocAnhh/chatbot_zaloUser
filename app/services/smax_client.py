import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_to_smax(sender_id: str, message: str, page_pid: str = None) -> None:
    # headers smax
    headers = {"Authorization": f"Bearer {settings.smax_api_token}"}
    
    # payload smax
    payload = {
        "customer": {
            "pid": sender_id,
            "page_pid": page_pid
        },
        "attrs": [
            {
                "name": "message",
                "value": message
            }
        ]
    }
    
    logger.info(f"Sending to SMAX - URL: {settings.smax_api_endpoint}")
    logger.info(f"Payload (JSON): {payload}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.smax_api_endpoint, 
                json=payload,
                headers=headers, 
                timeout=10
            )
            logger.info(f"SMAX response status: {response.status_code}")
            logger.info(f"SMAX response body: {response.text}")
            response.raise_for_status()
            logger.info(f"Message sent successfully to {sender_id}")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error sending message to {sender_id}: {e}")
        logger.error(f"Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
        logger.error(f"Response body: {e.response.text if hasattr(e, 'response') else 'N/A'}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending message to {sender_id}: {e}")
        raise