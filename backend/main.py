# Main entry point for the backend
from fastapi import FastAPI

app = FastAPI(title="AI Paper Marking API")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Paper Marking API"}
