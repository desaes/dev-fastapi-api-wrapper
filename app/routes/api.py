from fastapi import APIRouter
from app.src.endpoints import example as example

router = APIRouter()
router.include_router(example.router)