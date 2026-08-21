import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config.settings import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed.",
        )

    extension = ALLOWED_IMAGE_TYPES[file.content_type]

    filename = f"{secrets.token_hex(16)}{extension}"

    upload_directory = Path(
        settings.upload_dir
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = upload_directory / filename

    max_size = (
        settings.max_image_size_mb
        * 1024
        * 1024
    )

    total_size = 0

    try:
        with file_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > max_size:
                    file_path.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"Image must be smaller than "
                            f"{settings.max_image_size_mb} MB."
                        ),
                    )

                output.write(chunk)

        try:
            with Image.open(file_path) as image:
                image.verify()

        except (
            UnidentifiedImageError,
            OSError,
        ):
            file_path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file.",
            )

        return f"/uploads/posts/{filename}"

    except HTTPException:
        raise

    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image.",
        )

    finally:
        await file.close()


def delete_image(image_url: str) -> None:
    filename = Path(image_url).name

    file_path = (
        Path(settings.upload_dir)
        / filename
    )

    file_path.unlink(missing_ok=True)