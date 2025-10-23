from google import genai
from google.genai import types
from config import get_settings
from models import ComplaintCategory, Priority
from typing import Optional, Tuple
import json

settings = get_settings()

# Initialize Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def categorize_complaint(
    title: str,
    description: str,
    image_url: Optional[str] = None
) -> Tuple[ComplaintCategory, Priority]:
    """
    Use Gemini AI to categorize the complaint and determine priority
    Returns: (category, priority)
    """
    
    # Build the prompt
    prompt = f"""
Analyze this citizen complaint and provide:
1. Category: Choose ONE from [pothole, garbage, streetlight, drainage, water_leakage, power_outage, other]
2. Priority: Choose ONE from [low, medium, high, critical]

Title: {title}
Description: {description}

Consider:
- Safety hazards = high/critical priority
- Public health issues = high priority
- Infrastructure damage = medium/high priority
- Minor inconveniences = low/medium priority

Respond in JSON format:
{{"category": "category_name", "priority": "priority_level"}}
"""
    
    try:
        # Prepare content parts (URL-based image no longer used by default)
        content_parts = [prompt]
        
        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content_parts
        )
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response (handling markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        # Map to enums
        category_str = result.get("category", "other").lower()
        priority_str = result.get("priority", "medium").lower()
        
        # Convert to enum values
        category = ComplaintCategory(category_str) if category_str in [c.value for c in ComplaintCategory] else ComplaintCategory.OTHER
        priority = Priority(priority_str) if priority_str in [p.value for p in Priority] else Priority.MEDIUM
        
        return category, priority
        
    except Exception as e:
        print(f"Error in Gemini categorization: {e}")
        # Return default values on error
        return ComplaintCategory.OTHER, Priority.MEDIUM


async def categorize_complaint_with_image_bytes(title: str, description: str, image_bytes: bytes, mime_type: str = "image/jpeg"):
    prompt = f"""
Analyze this citizen complaint and provide:
1. Category: Choose ONE from [pothole, garbage, streetlight, drainage, water_leakage, power_outage, other]
2. Priority: Choose ONE from [low, medium, high, critical]

Title: {title}
Description: {description}

Respond in JSON format:
{{"category": "category_name", "priority": "priority_level"}}
"""
    parts = [prompt]
    if image_bytes:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=parts
    )
    # Parse response
    response_text = response.text.strip()
    
    # Extract JSON from response (handling markdown code blocks)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()
    
    result = json.loads(response_text or "{}")
    
    # Map to enums
    category_str = result.get("category", "other").lower()
    priority_str = result.get("priority", "medium").lower()
    
    # Convert to enum values
    category = ComplaintCategory(category_str) if category_str in [c.value for c in ComplaintCategory] else ComplaintCategory.OTHER
    priority = Priority(priority_str) if priority_str in [p.value for p in Priority] else Priority.MEDIUM
    
    return category, priority
        


async def analyze_with_audio(
    title: str,
    description: str,
    image_url: Optional[str] = None,
    audio_url: Optional[str] = None
) -> Tuple[ComplaintCategory, Priority, str]:
    """
    Enhanced analysis including audio transcription
    Returns: (category, priority, transcribed_text)
    """
    
    # For now, use the basic categorization
    # Audio transcription can be added later if needed
    category, priority = await categorize_complaint(title, description, image_url)
    
    return category, priority, ""


async def get_similar_complaint_embeddings(text: str):
    """
    Generate embeddings for similarity matching
    This can be used for duplicate detection
    """
    try:
        # Note: Gemini embeddings API would be used here
        # For hackathon, we'll use simpler location + category based matching
        pass
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

