from openai import AsyncOpenAI
from backend.config import settings
from backend.models import ExtractedContent

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def reconstruct_handwriting(extracted: ExtractedContent) -> str:
    """
    Takes raw extracted text (potentially messy/garbled from handwriting)
    and uses GPT-4o to:
    1. Clean up OCR artifacts
    2. Fix character-level errors
    3. Reconstruct coherent sentences
    4. Preserve the ORIGINAL language (Sinhala/Tamil/English)
    5. NOT translate — only clean and restructure
    """
    if not extracted.raw_extracted:
        return ""
        
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"This is {extracted.detected_language} handwritten text extracted via OCR. Clean up OCR artifacts, fix character-level errors, and reconstruct coherent sentences. Preserve the ORIGINAL language. Do NOT translate. Just return the clean text."
            },
            {
                "role": "user",
                "content": extracted.raw_extracted
            }
        ]
    )
    
    return response.choices[0].message.content.strip()
