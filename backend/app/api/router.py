from fastapi import APIRouter

from app.api.endpoints import system
from app.api.v1 import briefs

api_router = APIRouter(prefix="/api")
api_router.include_router(system.router)
api_router.include_router(briefs.router, prefix="/v1")
