from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routers import router as jars_router
from app.db import Base, engine
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="JarVault API", version="1.0.0", lifespan=lifespan)

app.include_router(jars_router, prefix="/api", tags=["jars"])