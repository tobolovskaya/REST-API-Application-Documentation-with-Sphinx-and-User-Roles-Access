from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db

from src.schemas import User
from src.conf.config import settings
from src.services.auth import get_current_user, get_current_admin_user
from src.services.users import UserService
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=User, description="No more than 10 requests per min")
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.

    Args:
        request (Request): The request object.
        user (User): The current authenticated user.

    Returns:
        User: The current authenticated user.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the current authenticated user.

    Args:
        file (UploadFile): The new avatar file.
        user (User): The current authenticated user.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    return await user_service.update_avatar_url(user.email, avatar_url)
