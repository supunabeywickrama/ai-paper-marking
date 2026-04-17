from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.database import engine
from backend.routes import students, exams, upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure we can connect to DB or handle other startup tasks
    yield
    # Shutdown: dispose the DB engine
    await engine.dispose()

app = FastAPI(title="AI Paper Marking API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: restrict to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists for static serving
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Paper Marking API"}

app.include_router(students.router)
app.include_router(exams.router)
app.include_router(upload.router)
