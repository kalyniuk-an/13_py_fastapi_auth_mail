from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

import cloudinary.uploader

from app.database import get_db
from app.models import User
from app.repository_users import update_avatar
from app.schemas import UserResponse
from app.services.auth import auth_service
from app.services.cloudinary_service import configure_cloudinary


router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed",
            )

        configure_cloudinary()

        result = cloudinary.uploader.upload(
            file.file,
            public_id=f"ContactsApp/{current_user.id}",
            overwrite=True,
            resource_type="image",
        )

        avatar_url = result.get("secure_url")

        if not avatar_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload avatar",
            )

        user = update_avatar(current_user, avatar_url, db)

        return user

    finally:
        await file.close()