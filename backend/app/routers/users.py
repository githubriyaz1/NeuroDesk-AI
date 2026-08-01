from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserResponse,
    UserProfileUpdate,
    ChangePasswordRequest,
)
from app.services.auth_service import auth_service
from app.routers.deps import get_current_active_user
from app.utils.response import success_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Retrieve current authenticated user details."""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user full name profile details."""
    return await auth_service.update_profile(db=db, current_user=current_user, profile_in=profile_in)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    pass_in: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify current password, update password hash, and revoke active sessions."""
    await auth_service.change_password(db=db, current_user=current_user, pass_in=pass_in)
    return success_response(message="Password changed successfully. Active sessions revoked.")


@router.delete("/delete-account", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete user account and revoke active sessions."""
    await auth_service.soft_delete_account(db=db, current_user=current_user)
    return success_response(message="Account deactivated successfully.")
