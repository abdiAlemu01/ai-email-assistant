# main.py

from fastapi import FastAPI
from .api.router import api_router

app = FastAPI(title="AI Email Assistant")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Email Assistant backend"}
