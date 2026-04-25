# AI-Powered Multilingual Intelligent Paper Marking System

An advanced exam marking platform that reads handwritten and printed answer sheets in **Sinhala, Tamil, and English**, evaluates them using GPT-4o Vision, generates annotated PDFs, and produces a fair time-aware leaderboard.

## Key Features

- **Multilingual OCR** — direct understanding of Sinhala, Tamil, and English handwriting (no forced translation)
- **Handwriting Reconstruction** — converts messy handwriting to clean structured text before evaluation
- **Visual Answer Evaluation** — recognises and marks graphs, tables, and diagrams
- **Time-Aware Submission** — ON_TIME submissions are ranked; late submissions are marked but excluded from rankings; rejected submissions are not processed
- **Annotated PDF Generation** — produces a corrected annotated paper and a clean rewritten answer sheet per submission
- **Email Notifications** — sends graded PDF and score to the student automatically
- **Admin Dashboard** — live stats, per-exam leaderboards, score distribution charts, and submission management

## Architecture

```
Next.js 16 Frontend (port 3000)
        │
FastAPI Backend (port 8000)
        │
   ┌────┴────┐
   │  GPT-4o │  (Vision + LLM)
   └────┬────┘
        │
   PostgreSQL (port 5433 via Docker)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0 async, Alembic |
| AI | OpenAI GPT-4o (Vision + structured output) |
| Image Processing | OpenCV, PyMuPDF (fitz) |
| PDF Generation | ReportLab, PyMuPDF |
| Database | PostgreSQL 15 |
| Email | SMTP (Gmail App Password) |

## Project Structure

```
ai-paper-marking/
├── backend/
│   ├── main.py                  # FastAPI app + CORS + router registration
│   ├── models.py                # SQLAlchemy ORM models (8 tables)
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── database.py              # Async engine + session factory
│   ├── config.py                # pydantic-settings (.env loader)
│   ├── routes/
│   │   ├── exams.py             # CRUD + generate-rankings + submissions by exam
│   │   ├── students.py          # Student CRUD
│   │   ├── upload.py            # Paper upload + pipeline trigger
│   │   ├── submissions.py       # Submissions + evaluations + PDFs
│   │   ├── rankings.py          # Leaderboard per exam
│   │   └── dashboard.py        # Aggregate stats
│   └── services/
│       ├── pipeline.py          # Orchestrates the full marking pipeline
│       ├── vision_reader.py     # GPT-4o Vision OCR per page
│       ├── text_rewriter.py     # Handwriting reconstruction
│       ├── evaluator.py         # Text answer evaluation
│       ├── visual_evaluator.py  # Graph/table/diagram evaluation
│       ├── diagram_detector.py  # Detect visual element types
│       ├── graph_analyzer.py    # Graph axis/trend analysis
│       ├── table_extractor.py   # Table row/column extraction
│       ├── annotation.py        # Annotate original PDF with marks
│       ├── pdf_generator.py     # Generate clean rewritten PDF
│       ├── email_service.py     # SMTP email with PDF attachment
│       ├── ranking_service.py   # Rank ON_TIME submissions by score
│       ├── marking_scheme_parser.py  # Parse uploaded marking scheme PDF
│       └── time_validator.py    # ON_TIME / LATE_ACCEPTED / REJECTED logic
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Dashboard
│   │   ├── exams/
│   │   │   ├── page.tsx         # Exam list + Create Exam modal
│   │   │   └── [id]/page.tsx    # Exam detail: Submissions | Rankings | Analytics
│   │   ├── submissions/
│   │   │   └── [id]/page.tsx    # Submission detail: scores + evaluation cards + PDF downloads
│   │   ├── rankings/[examId]/page.tsx  # Public leaderboard
│   │   └── upload/page.tsx      # Student paper upload form
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── StatsCard.tsx
│   │   ├── TimeStatusBadge.tsx  # ON_TIME / LATE / REJECTED pill
│   │   ├── EvaluationCard.tsx   # Per-question marks + feedback + key points
│   │   ├── SubmissionTable.tsx  # Sortable submissions table
│   │   ├── ExamForm.tsx         # Create exam modal
│   │   ├── ScoreChart.tsx       # Recharts score distribution bar chart
│   │   └── RankingTable.tsx     # Reusable ranking table
│   └── utils/
│       └── api.ts               # Axios instance (base URL: http://localhost:8000/api)
├── docker-compose.yml           # PostgreSQL 15 on port 5433
├── implementation_plan.md
└── user_manual.md
```

## Database Schema

| Table | Purpose |
|---|---|
| `exams` | Exam metadata + parsed marking scheme JSON |
| `students` | Student profiles with language preference |
| `submissions` | Upload record, time_status, processing_status, score |
| `extracted_content` | Per-question OCR output (text + visual metadata) |
| `evaluations` | Per-question marks, feedback, detailed reasoning |
| `generated_pdfs` | Paths to annotated and clean PDFs |
| `email_logs` | Email delivery status |
| `rankings` | Computed rank per ON_TIME submission |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/exams` | List all exams |
| `POST` | `/api/exams` | Create exam (multipart: title, subject, deadlines, PDF) |
| `GET` | `/api/exams/{id}` | Get exam by ID |
| `PUT` | `/api/exams/{id}` | Update exam fields |
| `DELETE` | `/api/exams/{id}` | Delete exam |
| `GET` | `/api/exams/{id}/submissions` | List submissions for an exam |
| `POST` | `/api/exams/{id}/generate-rankings` | Recompute rankings |
| `GET` | `/api/rankings/{exam_id}` | Get leaderboard for an exam |
| `POST` | `/api/upload` | Upload answer sheet (triggers pipeline) |
| `GET` | `/api/submissions` | List all submissions |
| `GET` | `/api/submissions/{id}` | Get submission by ID |
| `GET` | `/api/submissions/{id}/evaluations` | Per-question evaluation results |
| `GET` | `/api/submissions/{id}/pdfs` | Generated PDF download links |
| `GET` | `/api/students` | List all students |
| `POST` | `/api/students` | Create student |
| `GET` | `/api/dashboard/stats` | Aggregate dashboard statistics |

## Quick Start

See [user_manual.md](user_manual.md) for full setup and usage instructions.

```bash
# 1. Start the database (project root)
docker compose up -d

# 2. Install backend deps and start API (stay in project root after activating venv)
cd backend && pip install -r requirements.txt
cd ..
backend\venv\Scripts\Activate.ps1   # Windows PowerShell
# source backend/venv/bin/activate  # macOS / Linux
uvicorn backend.main:app --reload --port 8000

# 3. Start the frontend (new terminal, from project root)
cd frontend && npm install && npm run dev
```

> `uvicorn` must run from the **project root** (`ai-paper-marking/`), not from inside `backend/`. All internal imports use the `backend.` package prefix.

Open [http://localhost:3000](http://localhost:3000).

## Time-Based Submission Rules

| Submitted | Status | Marked | Ranked |
|---|---|---|---|
| Before deadline | ON_TIME | Yes | Yes |
| Deadline → Late deadline | LATE_ACCEPTED | Yes | No |
| After late deadline | REJECTED | No | No |
