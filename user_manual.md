# AI-Powered Multilingual Intelligent Paper Marking System - User Manual

## Overview
Welcome to the AI-Powered Multilingual Intelligent Paper Marking System! This platform allows administrators and students to seamlessly manage exams, upload handwritten or printed answer sheets (in Sinhala, Tamil, or English), and automatically evaluate them using advanced AI (GPT-4o Vision).

## Prerequisites
Before running the system, ensure you have:
1. **Docker Desktop** installed and running.
2. **Python 3.10+** installed.
3. An active **OpenAI API Key** with access to GPT-4o.
4. **Node.js** installed (for the frontend).

## Setup Instructions

### 1. Environment Configuration
Navigate to the `backend` folder and open the `.env` file. Fill in your details:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/aipapermarking
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
UPLOAD_DIR=./uploads
```

### 2. Start the Database
Open a terminal in the root folder (`ai-paper-marking`) and run:
```bash
docker compose up -d
```
This will start your PostgreSQL database on port 5433.

### 3. Setup the Backend
Navigate to the `backend` folder, install dependencies, and run the server:
```bash
cd backend
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload
```

## System Workflow
1. **Admin creates an Exam:** The admin uploads a marking scheme PDF and sets deadlines.
2. **Student uploads Paper:** Students upload their answer scripts (PDF/images) before the deadline.
3. **AI Evaluation Pipeline:** 
   - The system extracts text/visuals using OCR.
   - Reconstructs messy handwriting.
   - Evaluates answers against the marking scheme.
   - Generates an annotated PDF with corrections and feedback.
4. **Ranking & Notification:** Students receive an email with their graded PDF, and the dashboard updates with the leaderboard.

## Support
For any issues regarding missing dependencies, ensure that you have installed all packages listed in `requirements.txt` and that your Docker container is healthy.
