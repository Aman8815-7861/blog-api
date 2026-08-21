from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.posts import router as posts_router


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(auth_router)
router.include_router(posts_router)