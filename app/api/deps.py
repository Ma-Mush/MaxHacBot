"""API dependencies including database session and API key security."""
from typing import AsyncGenerator, Optional
from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
) -> str:
    """Verify X-API-Key header against configured APP_API_KEY.
    
    If settings.APP_API_KEY is unset or empty, auth is bypassed in dev mode.
    """
    if not settings.APP_API_KEY:
        return "bypassed"

    if not x_api_key or x_api_key != settings.APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key
