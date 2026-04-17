# ai-paper-marking

An AI-powered paper marking system that combines **vision AI** and **large language models** to evaluate both textual and visual student answers, while enforcing **time-based fairness** through automated ranking and intelligent marking.

---

## Features

| Feature | Description |
|---|---|
| 🔤 **Text marking** | Evaluates written answers using an LLM (GPT-4o) with structured feedback |
| 🖼️ **Vision marking** | Evaluates diagrams, sketches, and image answers using a vision model |
| 🔀 **Mixed answers** | Handles submissions containing both text and images |
| ⏰ **Time-based fairness** | Early-submission bonuses and late-submission penalties |
| 🏆 **Automated ranking** | Students ranked by marks; ties broken by submission time |
| 📊 **Detailed feedback** | Per-submission breakdown of content marks, presentation marks, and time adjustment |

---

## Architecture

```
app/
├── config.py               # Settings (loaded from env / .env file)
├── main.py                 # FastAPI application entry point
├── models/
│   └── submission.py       # Pydantic data models
├── services/
│   ├── text_marker.py      # LLM-based text answer evaluator
│   ├── vision_marker.py    # Vision-model image answer evaluator
│   ├── marking_engine.py   # Orchestrator (text / image / mixed)
│   ├── time_fairness.py    # Time-based mark adjustment calculator
│   └── ranking_engine.py   # Automated ranking builder
└── api/
    └── routes.py           # REST API endpoints
tests/
├── test_time_fairness.py   # Unit tests for time fairness logic
├── test_ranking_engine.py  # Unit tests for ranking logic
├── test_marking_engine.py  # Unit tests for marking orchestration
└── test_api_routes.py      # Integration tests for API endpoints
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- An OpenAI API key with access to `gpt-4o`

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and set your OpenAI key:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_TEXT=gpt-4o
OPENAI_MODEL_VISION=gpt-4o

# Time fairness
EARLY_SUBMISSION_BONUS_MINUTES=30
EARLY_SUBMISSION_BONUS_MARKS=2.0
LATE_SUBMISSION_PENALTY_PER_MINUTE=0.5
MAX_LATE_PENALTY=20.0

# Passing threshold
PASSING_MARKS=40.0
```

### Running the server

```bash
uvicorn app.main:app --reload
```

API documentation available at `http://localhost:8000/docs`.

---

## API Reference

### `POST /api/v1/mark`

Mark a student submission.

**Request body:**

```json
{
  "submission": {
    "student_id": "stu_001",
    "question_id": "q1",
    "exam_id": "exam_2024_biology",
    "answer_text": "Photosynthesis converts light energy into chemical energy...",
    "answer_image_base64": "<base64-encoded image or null>",
    "answer_type": "text",
    "submitted_at": "2024-06-01T11:30:00Z"
  },
  "criteria": {
    "question_id": "q1",
    "question_text": "Explain the process of photosynthesis.",
    "model_answer": "Photosynthesis is the process by which plants...",
    "max_marks": 20.0,
    "marking_rubric": "Award marks for: light reactions, Calvin cycle, products.",
    "deadline": "2024-06-01T12:00:00Z"
  }
}
```

**Response:**

```json
{
  "result": {
    "student_id": "stu_001",
    "marks_breakdown": {
      "content_marks": 14.0,
      "presentation_marks": 3.0,
      "time_adjustment": 2.0,
      "total_marks": 19.0,
      "max_marks": 20.0,
      "percentage": 95.0
    },
    "feedback": "Excellent explanation covering both light-dependent and independent reactions.",
    "strengths": ["Accurate description of Calvin cycle", "Good use of terminology"],
    "improvements": ["Could mention the role of chlorophyll"],
    "is_passing": true
  },
  "time_status": "Early (bonus applied)"
}
```

### `GET /api/v1/rankings/{exam_id}`

Get the automated ranking for an exam.

### `GET /api/v1/results/{exam_id}/{student_id}`

Get all marking results for a student in an exam.

---

## Time-Based Fairness

The system enforces fairness through configurable time rules:

| Scenario | Effect |
|---|---|
| Submitted ≥ 30 min before deadline | +2.0 bonus marks |
| Submitted < 30 min before deadline | No adjustment |
| Submitted exactly on deadline | No adjustment |
| Submitted late | −0.5 marks per minute (max −20.0) |
| Equal marks, different times | Earlier submitter ranked higher |

All thresholds are configurable via environment variables.

---

## Running Tests

```bash
python -m pytest tests/ -v
```
