from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.post import PostStatus


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    cover_image: str
    description: str
    content: str
    status: PostStatus
    author_id: UUID
    created_at: datetime
    updated_at: datetime


class PostUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content: str | None = None

