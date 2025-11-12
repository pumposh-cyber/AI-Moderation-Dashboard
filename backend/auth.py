"""Clerk authentication integration using JWT verification."""
import structlog
from fastapi import HTTPException, status, Depends, Header
from typing import Optional
import jwt
from jwt import PyJWKClient
from functools import lru_cache

from backend.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Cache for JWKS client
_jwks_client = None


@lru_cache()
def get_jwks_url() -> str:
    """Get Clerk JWKS URL from publishable key."""
    if not settings.clerk_publishable_key:
        return ""
    
    # Extract instance ID from publishable key (format: pk_test_xxx or pk_live_xxx)
    # JWKS URL format: https://<instance>.clerk.accounts.dev/.well-known/jwks.json
    key_parts = settings.clerk_publishable_key.split("_")
    if len(key_parts) >= 3:
        instance_id = key_parts[2]  # Extract instance identifier
        return f"https://{instance_id}.clerk.accounts.dev/.well-known/jwks.json"
    
    return ""


def get_jwks_client():
    """Get or create JWKS client for token verification."""
    global _jwks_client
    if _jwks_client is None and settings.clerk_enabled:
        jwks_url = get_jwks_url()
        if not jwks_url:
            logger.warning("Cannot determine JWKS URL from Clerk publishable key")
            return None
        
        try:
            _jwks_client = PyJWKClient(jwks_url)
            logger.info("JWKS client initialized", jwks_url=jwks_url)
        except Exception as e:
            logger.error("Failed to initialize JWKS client", error=str(e))
            return None
    
    return _jwks_client


async def verify_clerk_token(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Verify Clerk JWT token and return user information.
    
    Args:
        authorization: Authorization header value (Bearer token)
    
    Returns:
        dict: User information including user_id
    
    Raises:
        HTTPException: If authentication fails
    """
    # If Clerk is disabled, return a mock user for development
    if not settings.clerk_enabled:
        logger.debug("Clerk authentication disabled, using mock user")
        return {
            "user_id": "dev_user_123",
            "email": "dev@example.com",
            "first_name": "Dev",
            "last_name": "User"
        }
    
    # Check if authorization header is present
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token using JWKS
    jwks_client = get_jwks_client()
    if not jwks_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )
    
    try:
        # Get signing key from JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
            }
        )
        
        # Extract user information from token payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        email = payload.get("email")
        first_name = payload.get("given_name") or payload.get("first_name")
        last_name = payload.get("family_name") or payload.get("last_name")
        
        logger.debug("User authenticated", user_id=user_id)
        return {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error("Invalid token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Token verification failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency for protected routes
async def get_current_user(user: dict = Depends(verify_clerk_token)) -> dict:
    """Dependency to get current authenticated user."""
    return user
