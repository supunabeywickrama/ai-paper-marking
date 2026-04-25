# User Manual — AI-Powered Multilingual Intelligent Paper Marking System

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation & Setup](#2-installation--setup)
3. [Running the System](#3-running-the-system)
4. [Admin Workflows](#4-admin-workflows)
   - 4.1 [Creating an Exam](#41-creating-an-exam)
   - 4.2 [Viewing Submissions](#42-viewing-submissions)
   - 4.3 [Generating Rankings](#43-generating-rankings)
   - 4.4 [Viewing Analytics](#44-viewing-analytics)
   - 4.5 [Viewing a Submission Detail](#45-viewing-a-submission-detail)
5. [Student Workflows](#5-student-workflows)
   - 5.1 [Uploading an Answer Sheet](#51-uploading-an-answer-sheet)
6. [Understanding Results](#6-understanding-results)
   - 6.1 [Time Status](#61-time-status)
   - 6.2 [Evaluation Cards](#62-evaluation-cards)
   - 6.3 [Score Distribution Chart](#63-score-distribution-chart)
7. [Marking Scheme PDF Format](#7-marking-scheme-pdf-format)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

Before running the system, ensure you have installed:

| Requirement | Version |
|---|---|
| Docker Desktop | Latest |
| Python | 3.10+ |
| Node.js | 18+ |
| OpenAI API Key | GPT-4o access required |

---

## 2. Installation & Setup

### 2.1 Clone the Repository

```bash
git clone <your-repo-url>
cd ai-paper-marking
```

### 2.2 Configure the Backend Environment

Create `backend/.env` by copying the example below and filling in your values:

```env
OPENAI_API_KEY=sk-...your-key-here...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/aipapermarking
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
UPLOAD_DIR=./uploads
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App Passwords. Generate a password for "Mail". Use that 16-character password as `SMTP_PASSWORD`.

### 2.3 Set Up Backend Virtual Environment & Install Dependencies

**Create and activate a virtual environment:**

On **macOS / Linux**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

On **Windows** (Command Prompt):
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

On **Windows** (PowerShell):
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
```

> **Note:** If you get an execution policy error on Windows PowerShell, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Install dependencies:**
```bash
pip install -r requirements.txt
```

> **Deactivate:** When finished, deactivate the virtual environment with `deactivate`

### 2.4 Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## 3. Running the System

Open **three** terminal windows:

**Terminal 1 — Database**
```bash
# From the project root
docker compose up -d
```
This starts PostgreSQL on port `5433`. Data persists across restarts via a Docker volume.

**Terminal 2 — Backend API**

Activate the virtual environment, then run uvicorn **from the project root** (the `backend.` prefix requires the project root to be in `sys.path`):

On **Windows** (PowerShell):
```powershell
backend\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

On **macOS / Linux**:
```bash
source backend/venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

> **Common mistake:** Do not `cd backend` before running uvicorn. All internal imports use the `backend.` prefix, so the working directory must be the project root (`ai-paper-marking/`).

**Terminal 3 — Frontend**
```bash
cd frontend
npm run dev
```
The web app will be available at `http://localhost:3000`.

> **First run only:** The database tables are created automatically when the backend starts (SQLAlchemy `create_all`). No manual migration step is needed.

---

## 4. Admin Workflows

### 4.1 Creating an Exam

1. Navigate to **Exams** in the sidebar.
2. Click **Create New Exam**.
3. Fill in the form:
   - **Title** — e.g. "Mathematics Final 2025"
   - **Subject** — e.g. "Mathematics"
   - **Max Questions** — total number of questions in the exam
   - **Deadline** — the cutoff time for ON_TIME submissions
   - **Late Deadline** — the cutoff for LATE_ACCEPTED submissions (after this, submissions are REJECTED)
   - **Marking Scheme PDF** — upload the marking scheme file (see [Section 7](#7-marking-scheme-pdf-format) for the required format)
4. Click **Create Exam**. The PDF is parsed automatically by GPT-4o to extract questions, model answers, mark allocations, and answer types.

### 4.2 Viewing Submissions

1. Click on any exam **title** (or the **Manage** link) in the Exams list.
2. The **Submissions** tab shows all answer sheets received for that exam with:
   - Student UUID (truncated)
   - Submission date/time
   - Time status badge (ON_TIME / LATE / REJECTED)
   - Processing status (PENDING → PROCESSING → COMPLETED / FAILED)
   - Total score (once completed)
   - **View** link to the full submission detail
3. Click any column header arrow to sort the table.

### 4.3 Generating Rankings

1. From the exam detail page, click the **Rankings** tab.
2. Click **Generate Rankings**.
3. The system scores all COMPLETED, ON_TIME submissions and assigns ranks (ties share the same rank). LATE_ACCEPTED submissions are marked but not included in the leaderboard.
4. Rankings are also viewable from the public **Leaderboard** page at `/rankings/{examId}`.

### 4.4 Viewing Analytics

1. From the exam detail page, click the **Analytics** tab.
2. A bar chart shows the score distribution across five buckets: 0–20, 21–40, 41–60, 61–80, 81–100.
3. Only COMPLETED submissions appear in the chart.

### 4.5 Viewing a Submission Detail

1. From the Submissions tab, click **View** on any row.
2. The detail page shows:
   - **Header** — exam name, submission time, time status, processing status, total score
   - **PDF Downloads** — Annotated PDF (original paper with AI corrections overlaid) and Clean PDF (rewritten clean answer sheet)
   - **Question Breakdown** — one Evaluation Card per question (see [Section 6.2](#62-evaluation-cards))

---

## 5. Student Workflows

### 5.1 Uploading an Answer Sheet

1. Navigate to **Upload Paper** in the sidebar.
2. Select the exam from the dropdown.
3. Enter your **Student ID** (the UUID assigned to your student account — ask your administrator).
4. Upload your answer sheet: accepted formats are **PDF, PNG, JPG** (max 10 MB).
5. Click **Submit Paper**.

The system immediately checks the submission time:
- If before the exam deadline → **ON_TIME**, will be marked and ranked.
- If between deadline and late deadline → **LATE_ACCEPTED**, will be marked but not ranked.
- If after the late deadline → **REJECTED**, not processed.

Processing happens in the background (typically 1–3 minutes depending on the number of questions and whether visual answers are present). An email with your score and the graded PDF is sent to the email address on your student account once complete.

---

## 6. Understanding Results

### 6.1 Time Status

| Badge | Colour | Meaning |
|---|---|---|
| **On Time** | Green | Submitted before the deadline. Marked + ranked. |
| **Late** | Amber | Submitted between deadline and late deadline. Marked but not ranked. |
| **Rejected** | Red | Submitted after the late deadline. Not processed. |

### 6.2 Evaluation Cards

Each question in the submission detail shows an evaluation card with:

- **Question label** — e.g. Q1, Q2a, Q3b
- **Score bar** — visual progress bar coloured green (≥70%), amber (40–69%), or red (<40%)
- **Marks awarded / Max marks** — e.g. 8/10
- **Feedback** — the AI's explanation of the mark
- **Key Points Covered** — what the student answered correctly
- **Key Points Missed** — what was absent or incorrect

### 6.3 Score Distribution Chart

The Analytics tab shows a colour-coded histogram:

| Bucket | Colour |
|---|---|
| 0–20 | Red |
| 21–40 | Orange |
| 41–60 | Yellow |
| 61–80 | Green |
| 81–100 | Blue |

---

## 7. Marking Scheme PDF Format

The marking scheme PDF must be structured so GPT-4o can parse it. The recommended format is a clearly labelled document where each question appears on its own line or section:

```
Question 1 (10 marks) [TEXT]
Model Answer: The mitochondria is the powerhouse of the cell. It produces ATP through...

Question 2a (5 marks) [TEXT]
Model Answer: Newton's second law states F = ma...

Question 3 (8 marks) [VISUAL - GRAPH]
Model Answer: A correctly labelled line graph showing increasing temperature over time...
```

**Rules:**
- Each question must have a `marks` value.
- Each question should indicate its `answer_type`: `TEXT` (default) or `VISUAL` (for graphs, tables, diagrams).
- Model answers should be detailed — the AI uses them directly for comparison.
- If `answer_type` is `VISUAL`, the system uses the visual understanding pipeline instead of text evaluation.

---

## 8. Troubleshooting

**Backend fails to start — "relation does not exist"**
The database tables haven't been created yet. Make sure the Docker container is running first (`docker compose up -d`), then restart the backend.

**Submission stuck at PROCESSING**
Check the backend terminal for errors. Common causes:
- OpenAI API key is invalid or has no GPT-4o access
- The uploaded file is corrupted or not a valid PDF/image
- The marking scheme was not parsed correctly (check `/api/exams/{id}` → `marking_scheme_parsed`)

**Email not received**
- Verify `SMTP_USERNAME` and `SMTP_PASSWORD` in `backend/.env`
- Gmail requires a 16-character **App Password** (not your regular account password)
- Check the `email_logs` table via the API or database for the error message

**Submission marked FAILED**
The pipeline encountered an error. Check the backend logs for `Pipeline error for submission {id}:`. The most common cause is a malformed marking scheme JSON (the GPT-4o parser returned unexpected fields). Re-create the exam with a cleaner marking scheme PDF.

**Rankings not updating**
Rankings are not computed automatically after every submission — click **Generate Rankings** from the exam's Rankings tab to recompute.

**Frontend shows no data / CORS error**
Ensure the backend is running on port `8000`. The frontend Axios client is pre-configured to call `http://localhost:8000/api`. Check `frontend/utils/api.ts` if you're running on a different port.
