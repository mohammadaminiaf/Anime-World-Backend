from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
import os
from typing import Optional
from fastapi import UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import uuid4
from app.utils.upload_file import save_uploaded_file
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

from app.db.database import get_db
from app.models.user import UserDB, UserImagesDB
from app.schemas.users import UserCreate, Token
from app.schemas.users import LoginRequest, ChangePassword

router = APIRouter(prefix="/auth", tags=["auth"])


# Home page
@router.get("/")
def index():
    return "Hello World"


#! Create account
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("Route Register called")
    # Check if username or email already exist
    existing_user = (
        db.query(UserDB)
        .filter((UserDB.username == user.username) | (UserDB.email == user.email))
        .first()
    )

    # If user exists
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Generate a UUID for the user
    user_id = str(uuid4())

    # Hash the password
    hashed_pass = hash_password(user.password)

    # Create new user
    new_user = UserDB(
        id=user_id,
        name=user.name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        is_authenticated=False,
    )

    new_user.password = hashed_pass
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create a JWT token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "data": new_user.to_dict(),
        "access_token": access_token,
        "token_type": "bearer",
        "status_code": 200,
        "message": "Login successful",
    }


#! Log the user in
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Fetch current user from the database
    user = db.query(UserDB).filter(UserDB.username == login_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User could not be found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the password (if user exists ofc)
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a JWT token
    access_token = create_access_token(data={"sub": user.id})
    return {
        "data": user.to_dict(),
        "access_token": access_token,
        "token_type": "bearer",
        "status_code": 200,
        "message": "Login successful",
    }


#! Sign user out
@router.post("/logout", response_model=Token)
def logout():
    return {
        "data": None,
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "Logout successful",
    }


#! Change password
@router.post("/change-password", response_model=Token)
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthenticated"
        )

    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
        
    print('Checking password ************************************************************')

    # Verify user's current password is correct
    if not verify_password(data.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your old password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print('Password successfully checked ************************************************************')
        
    user.password = hash_password(data.new_password)
    db.commit()
    db.refresh(user)
    
    return {
        "data": {
            "data": True,    
        },
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "Password changes successfully!",
    }

#! Update Profile
@router.post(
    "/update-profile/{user_id}",
    response_model=Token,
)
def update(
    user_id: str,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    is_authenticated: Optional[bool] = Form(False),
    profile_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # Validate token
):

    current_user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    print(f"Fetched user {current_user}")

    if profile_photo is not None:
        # Save uploaded file and update profile photo
        file_path = save_uploaded_file(profile_photo, "users")

        if current_user.profile_photo:
            # Delete old photo from storage
            if os.path.exists(current_user.profile_photo.image_url):
                os.remove(current_user.profile_photo.image_url)

            # Update existing profile photo record
            current_user.profile_photo.image_url = file_path
        else:
            # Create a new profile photo record
            new_image = UserImagesDB(user_id=user_id, image_url=file_path)
            db.add(new_image)

    # Update user info of current user
    if name:
        current_user.name = name
    if email:
        current_user.email = email
    if phone:
        current_user.phone = phone
    if is_authenticated:
        current_user.is_authenticated = is_authenticated

    db.commit()
    db.refresh(current_user)

    return {
        "data": current_user.to_dict(),
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "Profile updated successfully",
    }


@router.get("/user/{user_id}", response_model=Token)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Use could not be found",
        )

    return {
        "data": user.to_dict(),
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "User retrieved successfully",
    }


#! Delete a user
@router.delete("/user/{user_id}", response_model=Token)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Fetch user
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User could not be found",
        )

    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You do not own this user")

    # # Delete associated products and media
    # user_products = db.query(ProductsDB).filter(ProductsDB.user_id == user_id).all()
    # for product in user_products:
    #     # Fetch and delete associated media for each product
    #     product_media = (
    #         db.query(ProductImagesDB)
    #         .filter(ProductImagesDB.product_id == product.id)
    #         .all()
    #     )
    #     for media in product_media:
    #         # Delete the media file (adjust if using cloud storage)
    #         if os.path.exists(media.image_url):
    #             os.remove(media.image_url)
    #         db.delete(media)

    #     # Delete the product itself
    #     db.delete(product)

    # Delete the user's profile image if exists
    if user.profile_photo and os.path.exists(user.profile_photo.image_url):
        os.remove(user.profile_photo.image_url)

    # Delete the user account
    db.delete(user)

    # Commit the changes
    db.commit()

    return {
        "data": None,
        "access_token": None,
        "token_type": None,
        "status_code": 200,
        "message": "User and all associated data were deleted successfully.",
    }
