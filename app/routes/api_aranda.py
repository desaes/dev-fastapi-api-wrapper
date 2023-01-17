from fastapi import APIRouter
from app.src.endpoints import token as token
from app.src.endpoints import whoami as whoami

router = APIRouter()
router.include_router(token.router)
router.include_router(whoami.router)