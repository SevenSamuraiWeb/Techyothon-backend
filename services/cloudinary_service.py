import cloudinary
import cloudinary.uploader
from config import get_settings
from fastapi import UploadFile
from typing import Optional
import io

settings = get_settings()

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


async def upload_image(file: UploadFile) -> Optional[str]:
    """
    Upload image to Cloudinary
    Returns the secure URL of the uploaded image
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="complaints/images",
            resource_type="image"
        )
        
        return result.get("secure_url")
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


async def upload_audio(file: UploadFile) -> Optional[str]:
    """
    Upload audio file to Cloudinary
    Returns the secure URL of the uploaded audio
    """
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="complaints/audio",
            resource_type="video"  # Cloudinary uses 'video' type for audio files
        )
        
        return result.get("secure_url")
    except Exception as e:
        print(f"Error uploading audio: {e}")
        return None


async def delete_file(public_id: str, resource_type: str = "image") -> bool:
    """
    Delete a file from Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

