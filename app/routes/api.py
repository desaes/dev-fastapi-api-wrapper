from fastapi import APIRouter
from src.endpoints import token as token

router = APIRouter()
router.include_router(token.router)