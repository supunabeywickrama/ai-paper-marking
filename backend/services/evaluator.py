import json
from openai import AsyncOpenAI
from backend.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def evaluate_text_answer(
    question: str,
    model_answer: str,
    student_answer: str,
    max_marks: float,
    language: str
) -> dict:
    """
    Uses GPT-4o to evaluate the student's text answer against the model answer.
    """
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert examiner. Evaluate the student's text answer against the model answer. Language: {language}. Maximum marks: {max_marks}. Question: {question}. Return structured evaluation."
            },
            {
                "role": "user",
                "content": f"Model Answer: {model_answer}\nStudent Answer: {student_answer}"
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "marks_awarded": {"type": "number"},
                        "feedback": {"type": "string"},
                        "correct_answer": {"type": "string"},
                        "detailed_reasoning": {
                            "type": "object",
                            "properties": {
                                "key_points_covered": {"type": "array", "items": {"type": "string"}},
                                "key_points_missed": {"type": "array", "items": {"type": "string"}},
                                "accuracy": {"type": "string"}
                            },
                            "required": ["key_points_covered", "key_points_missed", "accuracy"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["marks_awarded", "feedback", "correct_answer", "detailed_reasoning"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )
    
    return json.loads(response.choices[0].message.content)
