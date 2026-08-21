import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user, require_admin
from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User, UserRole
from app.schemas.post import PostResponse
from app.services.post import (
    create_post,
    delete_post,
    get_all_posts,
    get_post_by_id,
    publish_post,
    unpublish_post,
    update_post,
)


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def save_cover_image(
    file: UploadFile,
) -> str:
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG and WEBP images are allowed",
        )

    upload_dir = Path(settings.upload_dir) / "posts"
    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    extension = Path(file.filename or "").suffix.lower()

    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image extension",
        )

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = upload_dir / filename

    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/uploads/posts/{filename}"


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_blog_post(
    title: str = Form(...),
    description: str = Form(...),
    content: str = Form(...),
    cover_image: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    image_url = save_cover_image(cover_image)

    return create_post(
        db=db,
        title=title,
        cover_image=image_url,
        description=description,
        content=content,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[PostResponse],
)
def get_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_all_posts(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
def get_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post_by_id(
        db=db,
        post_id=post_id,
        current_user=current_user,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
def update_blog_post(
    post_id: uuid.UUID,
    title: str | None = Form(None),
    description: str | None = Form(None),
    content: str | None = Form(None),
    cover_image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_url = None

    if cover_image is not None:
        image_url = save_cover_image(cover_image)

    post = update_post(
        db=db,
        post_id=post_id,
        current_user=current_user,
        title=title,
        description=description,
        content=content,
        cover_image=image_url,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you do not have permission",
        )

    return post


@router.patch(
    "/{post_id}/publish",
    response_model=PostResponse,
)
def publish_blog_post(
    post_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    post = publish_post(
        db=db,
        post_id=post_id,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.patch(
    "/{post_id}/unpublish",
    response_model=PostResponse,
)
def unpublish_blog_post(
    post_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    post = unpublish_post(
        db=db,
        post_id=post_id,
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_blog_post(
    post_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    deleted = delete_post(
        db=db,
        post_id=post_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return None

