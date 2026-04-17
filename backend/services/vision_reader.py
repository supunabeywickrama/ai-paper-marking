import fitz
import cv2
import numpy as np
import base64
import json
from openai import AsyncOpenAI
from backend.config import settings
from backend.models import Exam, ExtractedContent

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def extract_content_from_pages(file_path: str, exam: Exam) -> list[ExtractedContent]:
    """
    1. Convert PDF pages to images (PyMuPDF)
    2. Pre-process images (OpenCV: deskew, contrast, denoise)
    3. Send each page to GPT-4o Vision with structured prompt
    4. Parse structured response into ExtractedContent records
    5. Return list of extracted content per question
    """
    doc = fitz.open(file_path)
    extracted_contents = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # Simple pre-processing (convert RGBA to RGB)
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            
        _, buffer = cv2.imencode('.png', img_array)
        base64_image = base64.b64encode(buffer).decode('utf-8')
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Extract handwritten and printed text from this exam paper. Identify question numbers and parts. Flag diagrams, graphs, or tables. Detect the language (si/ta/en)."
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
                    "name": "extracted_page",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question_number": {"type": "integer"},
                                        "question_part": {"type": ["string", "null"]},
                                        "content_type": {"type": "string", "enum": ["TEXT", "DIAGRAM", "GRAPH", "TABLE"]},
                                        "raw_extracted": {"type": ["string", "null"]},
                                        "detected_language": {"type": ["string", "null"]},
                                        "visual_metadata": {"type": ["object", "null"]}
                                    },
                                    "required": ["question_number", "question_part", "content_type", "raw_extracted", "detected_language", "visual_metadata"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["items"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
        
        page_data = json.loads(response.choices[0].message.content)
        for item in page_data["items"]:
            extracted_contents.append(
                ExtractedContent(
                    question_number=item["question_number"],
                    question_part=item["question_part"],
                    content_type=item["content_type"],
                    raw_extracted=item["raw_extracted"],
                    detected_language=item["detected_language"],
                    visual_metadata=item["visual_metadata"]
                )
            )
            
    return extracted_contents
