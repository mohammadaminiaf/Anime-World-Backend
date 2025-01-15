import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.routers.auth import get_current_user
from app.schemas.users import Token
from app.models.user import UserDB, UserImagesDB
from app.utils.upload_file import save_uploaded_file

router = APIRouter(tags=["auth"])


@router.put("/user/{user_id}", response_model=Token)
async def update_profile(
    user_id: str,
    name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    is_authenticated: bool = Form(False),
    profile_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    # Ensure user exists
    existing_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate ownership
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized to update this user")

    # Handle profile photo update
    if profile_photo is not None:
        # Save uploaded file and update profile photo
        file_path = save_uploaded_file(profile_photo, "users")
        
        print(f'Uploaded file path {file_path}')

        if existing_user.profile_photo:
            # Delete old photo from storage
            if os.path.exists(existing_user.profile_photo.image_url):
                os.remove(existing_user.profile_photo.image_url)

            # Update existing profile photo record
            existing_user.profile_photo.image_url = file_path
        else:
            # Create a new profile photo record
            new_image = UserImagesDB(user_id=user_id, image_url=file_path)
            db.add(new_image)

    # Update user fields dynamically
    existing_user.name = name
    existing_user.email = email
    existing_user.phone = phone
    existing_user.is_authenticated = is_authenticated

    # Commit changes
    db.commit()
    db.refresh(existing_user)

    return {
        "data": existing_user.to_dict(),
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "Profile updated successfully",
    }
