from fastapi import APIRouter

from src.api import data
from src.api import fraud

router = APIRouter()

router.include_router(data.router)

router.include_router(fraud.router)
