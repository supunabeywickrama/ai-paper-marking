import base64
import json
from openai import AsyncOpenAI
from backend.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def detect_and_classify_visuals(image_bytes: bytes) -> list[dict]:
    """
    Uses GPT-4o Vision to detect visual elements in a page:
    - Diagrams (circuits, biology diagrams, etc.)
    - Graphs (line, bar, pie charts)
    - Tables (data tables)
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Analyze this image and identify all distinct visual elements such as DIAGRAMs, GRAPHs, or TABLEs. Return a list of elements with their type and a detailed description."
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
                "name": "visual_elements",
                "schema": {
                    "type": "object",
                    "properties": {
                        "elements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["DIAGRAM", "GRAPH", "TABLE"]},
                                    "description": {"type": "string"}
                                },
                                "required": ["type", "description"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["elements"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)["elements"]
