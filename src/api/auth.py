from fastapi import Header, HTTPException, status
from src.config import Config

async def verify_api_key(x_api_key: str = Header(...)):
    """
    验证请求头中的 X-API-Key
    """
    if x_api_key != Config.API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return x_api_key