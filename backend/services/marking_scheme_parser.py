import base64
import json
import fitz  # PyMuPDF
from openai import AsyncOpenAI
from backend.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def parse_marking_scheme_pdf(file_path: str) -> dict:
    """
    1. Convert marking scheme PDF pages to images (PyMuPDF)
    2. Send to GPT-4o Vision with structured output schema
    3. Extract: question numbers, sub-parts, model answers,
       max marks per question, answer type (TEXT/VISUAL)
    4. Return structured JSON stored in exam.marking_scheme_parsed
    """
    doc = fitz.open(file_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        images.append(base64_image)
        
    messages = [
        {
            "role": "system",
            "content": "You are a specialized marking scheme parser. Extract the questions, sub-parts, answers, maximum marks, and specify if the expected answer is TEXT or VISUAL."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Parse this marking scheme into structured data."}
            ]
        }
    ]
    
    for img in images:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img}"
            }
        })
        
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "marking_scheme",
                "schema": {
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question_number": {"type": "integer"},
                                    "question_part": {"type": ["string", "null"]},
                                    "model_answer": {"type": "string"},
                                    "max_marks": {"type": "number"},
                                    "answer_type": {"type": "string", "enum": ["TEXT", "VISUAL"]}
                                },
                                "required": ["question_number", "question_part", "model_answer", "max_marks", "answer_type"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["questions"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)
