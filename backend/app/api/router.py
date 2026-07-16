# router.py

from fastapi import APIRouter
from .routes import email, auth, agent, review

api_router = APIRouter()

api_router.include_router(email.router)
api_router.include_router(auth.router)
api_router.include_router(agent.router)
api_router.include_router(review.router)
