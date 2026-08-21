from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.config.settings import settings


app = FastAPI(
    title="Blog API",
)

app.include_router(router)

app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_dir),
    name="uploads",
)