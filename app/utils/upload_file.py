import os
from uuid import uuid4
from fastapi import UploadFile, HTTPException

# Define the directory for uploads
UPLOADS_DIR = "uploads"

def save_uploaded_file(file: UploadFile, category: str) -> str:
    """
    Save an uploaded file to the local file system.

    Args:
        file (UploadFile): The uploaded file from the client.

    Returns:
        str: The relative path to the saved file.

    Raises:
        HTTPException: If the file is not an image or cannot be saved.
    """
    full_dir = f'{UPLOADS_DIR}/{category}'
    # Ensure the directory exists
    os.makedirs(full_dir, exist_ok=True)

    # Generate a unique filename
    unique_filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(full_dir, unique_filename)

    # Save the file to the uploads directory
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    finally:
        file.file.close()

    # Return the relative path for storage in the database
    return file_path
