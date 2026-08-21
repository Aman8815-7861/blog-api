import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.models.user import User, UserRole


def create_post(
    db: Session,
    title: str,
    cover_image: str,
    description: str,
    content: str,
    current_user: User,
) -> Post:
    post = Post(
        title=title,
        cover_image=cover_image,
        description=description,
        content=content,
        status=PostStatus.DRAFT,
        author_id=current_user.id,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def get_all_posts(
    db: Session,
    current_user: User,
) -> list[Post]:
    query = select(Post)

    # Admin can see drafts and published posts.
    if current_user.role == UserRole.ADMIN:
        query = query.order_by(Post.created_at.desc())

    # Normal users can see only published posts.
    else:
        query = (
            query
            .where(Post.status == PostStatus.PUBLISHED)
            .order_by(Post.created_at.desc())
        )

    return list(db.scalars(query).all())


def get_post_by_id(
    db: Session,
    post_id: uuid.UUID,
    current_user: User,
) -> Post | None:
    post = db.get(Post, post_id)

    if not post:
        return None

    # Admin can view both draft and published posts.
    if current_user.role == UserRole.ADMIN:
        return post

    # Normal users cannot view drafts.
    if post.status != PostStatus.PUBLISHED:
        return None

    return post


def update_post(
    db: Session,
    post_id: uuid.UUID,
    current_user: User,
    title: str | None = None,
    description: str | None = None,
    content: str | None = None,
    cover_image: str | None = None,
) -> Post | None:
    post = db.get(Post, post_id)

    if not post:
        return None

    # Only the author or admin can update.
    if (
        current_user.role != UserRole.ADMIN
        and post.author_id != current_user.id
    ):
        return None

    if title is not None:
        post.title = title

    if description is not None:
        post.description = description

    if content is not None:
        post.content = content

    if cover_image is not None:
        post.cover_image = cover_image

    db.commit()
    db.refresh(post)

    return post


def publish_post(
    db: Session,
    post_id: uuid.UUID,
) -> Post | None:
    post = db.get(Post, post_id)

    if not post:
        return None

    post.status = PostStatus.PUBLISHED

    db.commit()
    db.refresh(post)

    return post


def unpublish_post(
    db: Session,
    post_id: uuid.UUID,
) -> Post | None:
    post = db.get(Post, post_id)

    if not post:
        return None

    post.status = PostStatus.DRAFT

    db.commit()
    db.refresh(post)

    return post


def delete_post(
    db: Session,
    post_id: uuid.UUID,
) -> bool:
    post = db.get(Post, post_id)

    if not post:
        return False

    db.delete(post)
    db.commit()

    return True

