from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services.auth_service import auth_service
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """User registration endpoint enforcing email uniqueness and strong passwords."""
    return await auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """User login endpoint issuing JWT Access Token & Refresh Token."""
    return await auth_service.authenticate_user(db=db, credentials=credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Rotates refresh token and issues new access token pair."""
    return await auth_service.refresh_tokens(db=db, raw_refresh_token=req.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Revokes refresh token session."""
    await auth_service.logout_user(db=db, raw_refresh_token=req.refresh_token)
    return success_response(message="Logged out successfully")
