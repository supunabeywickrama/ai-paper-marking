import base64
import json
from openai import AsyncOpenAI
from backend.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def analyze_graph(image_bytes: bytes, question_context: str) -> dict:
    """
    GPT-4o Vision analyzes a graph to detect axes, units, data points, and trends.
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"Analyze this graph based on the context: {question_context}. Extract axes, units, and key trends."
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
                "name": "graph_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "x_axis": {"type": "string"},
                        "y_axis": {"type": "string"},
                        "trend": {"type": "string"},
                        "key_points": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["x_axis", "y_axis", "trend", "key_points"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)
