from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_raw_refresh_token,
    hash_token,
)
from app.core.config import settings
from app.core.logging import logger


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class AuthService:
    """Enterprise Business Logic Service for User Registration, Authentication, and Token Management."""

    async def register_user(self, db: AsyncSession, user_in: UserRegister) -> UserResponse:
        """Register a new user after validating email uniqueness."""
        stmt = select(User).where(User.email == user_in.email.lower())
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        hashed_pwd = get_password_hash(user_in.password)
        now = datetime.now(timezone.utc)
        new_user = User(
            email=user_in.email.lower(),
            full_name=user_in.full_name,
            password_hash=hashed_pwd,
            role="user",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        
        logger.info(f"Successfully registered user: {new_user.email} [{new_user.id}]")
        return UserResponse.model_validate(new_user)

    async def authenticate_user(self, db: AsyncSession, credentials: UserLogin) -> TokenResponse:
        """Authenticate user by email/password, record last_login, and generate access/refresh token pair."""
        stmt = select(User).where(User.email == credentials.email.lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account has been disabled.",
            )

        now = datetime.now(timezone.utc)
        user.last_login = now
        db.add(user)

        access_token = create_access_token(subject=user.id)
        raw_refresh_token = generate_raw_refresh_token()
        refresh_token_hash = hash_token(raw_refresh_token)
        refresh_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=refresh_expires,
            revoked=False,
            created_at=now,
        )
        db.add(db_refresh_token)
        await db.flush()

        logger.info(f"Authenticated user: {user.email} [{user.id}]")
        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    async def refresh_tokens(self, db: AsyncSession, raw_refresh_token: str) -> TokenResponse:
        """Rotates refresh token by revoking the old token and issuing a new token pair."""
        token_h = hash_token(raw_refresh_token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_h)
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if not token_record or token_record.revoked or _ensure_utc(token_record.expires_at) < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid, revoked, or expired.",
            )

        user_stmt = select(User).where(User.id == token_record.user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Associated user account is inactive or missing.",
            )

        token_record.revoked = True
        db.add(token_record)

        new_access_token = create_access_token(subject=user.id)
        new_raw_refresh_token = generate_raw_refresh_token()
        new_token_hash = hash_token(new_raw_refresh_token)
        new_expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=new_expires,
            revoked=False,
            created_at=now,
        )
        db.add(new_refresh_record)
        await db.flush()

        logger.info(f"Rotated refresh token for user: {user.email}")
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    async def logout_user(self, db: AsyncSession, raw_refresh_token: str) -> None:
        """Revokes specific refresh token session."""
        token_h = hash_token(raw_refresh_token)
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_h)
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if token_record:
            token_record.revoked = True
            db.add(token_record)
            await db.flush()
            logger.info(f"Revoked refresh token for user_id: {token_record.user_id}")

    async def update_profile(self, db: AsyncSession, current_user: User, profile_in: UserProfileUpdate) -> UserResponse:
        """Update user profile information."""
        if profile_in.full_name:
            current_user.full_name = profile_in.full_name
        
        current_user.updated_at = datetime.now(timezone.utc)
        db.add(current_user)
        await db.flush()
        await db.refresh(current_user)
        
        logger.info(f"Updated profile for user: {current_user.email}")
        return UserResponse.model_validate(current_user)

    async def change_password(self, db: AsyncSession, current_user: User, pass_in: ChangePasswordRequest) -> None:
        """Verify current password and set new password hash."""
        if not verify_password(pass_in.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password verification failed.",
            )

        current_user.password_hash = get_password_hash(pass_in.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        db.add(current_user)

        stmt = update(RefreshToken).where(RefreshToken.user_id == current_user.id).values(revoked=True)
        await db.execute(stmt)
        await db.flush()
        logger.info(f"Password changed and active sessions revoked for user: {current_user.email}")

    async def soft_delete_account(self, db: AsyncSession, current_user: User) -> None:
        """Soft delete user account by setting is_active=False and revoking sessions."""
        current_user.is_active = False
        current_user.updated_at = datetime.now(timezone.utc)
        db.add(current_user)

        stmt = update(RefreshToken).where(RefreshToken.user_id == current_user.id).values(revoked=True)
        await db.execute(stmt)
        await db.flush()
        logger.info(f"Soft deleted account for user: {current_user.email}")


auth_service = AuthService()
