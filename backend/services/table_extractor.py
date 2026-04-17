import base64
import json
from openai import AsyncOpenAI
from backend.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def extract_table(image_bytes: bytes) -> dict:
    """
    GPT-4o Vision extracts table data into structured JSON format.
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Extract the data from this table exactly as shown."
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "table_extraction",
                "schema": {
                    "type": "object",
                    "properties": {
                        "headers": {"type": "array", "items": {"type": "string"}},
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "required": ["headers", "rows"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)
