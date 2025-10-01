from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import get_db
from .models import Jar
from .schemas import JarOut
from .storage import JarStorage
from .config import settings

router = APIRouter()


@router.post("/jars", response_model=JarOut, status_code=201)
async def create_jar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".jar"):
        raise HTTPException(status_code=400, detail="File must be a .jar")

    storage = JarStorage()

    sha256 = storage.compute_sha256(file.file)

    # Enforce uniqueness by hash
    existing = db.execute(select(Jar).where(Jar.sha256 == sha256)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="A JAR with same content already exists")

    final_name, size_bytes = storage.save_file(file.file, file.filename, sha256)

    jar = Jar(
        name=final_name,
        sha256=sha256,
        size_bytes=size_bytes,
    )
    db.add(jar)
    db.commit()
    db.refresh(jar)
    return jar


@router.post("/jars/bulk", response_model=List[JarOut], status_code=201)
async def create_jars_bulk(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    storage = JarStorage()
    uploads: List[UploadFile] = []
    if files:
        uploads.extend(files)
    if file:
        uploads.extend(file)

    if not uploads:
        raise HTTPException(status_code=400, detail="No files provided. Use 'files' or 'file' fields.")

    created: List[Jar] = []

    for up in uploads:
        if not up.filename or not up.filename.lower().endswith(".jar"):
            continue
        sha256 = storage.compute_sha256(up.file)
        existing = db.execute(select(Jar).where(Jar.sha256 == sha256)).scalar_one_or_none()
        if existing:
            continue
        final_name, size_bytes = storage.save_file(up.file, up.filename, sha256)
        jar = Jar(name=final_name, sha256=sha256, size_bytes=size_bytes)
        db.add(jar)
        created.append(jar)

    if created:
        db.commit()
        for jar in created:
            db.refresh(jar)

    return created


@router.get("/jars", response_model=List[JarOut])
async def list_jars(db: Session = Depends(get_db)):
    rows = db.execute(select(Jar).order_by(Jar.created_at.desc())).scalars().all()
    return rows


@router.get("/jars/{jar_id}", response_model=JarOut)
async def get_jar(jar_id: int, db: Session = Depends(get_db)):
    jar = db.get(Jar, jar_id)
    if not jar:
        raise HTTPException(status_code=404, detail="Jar not found")
    return jar


@router.delete("/jars/{jar_id}", status_code=204)
async def delete_jar(
    jar_id: int,
    password: str = Query(..., description="Access password to authorize deletion"),
    db: Session = Depends(get_db),
):
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    if not settings.delete_password:
        raise HTTPException(status_code=500, detail="Server misconfigured: PASSWORD not set")
    if password != settings.delete_password:
        raise HTTPException(status_code=403, detail="Invalid password")

    jar = db.get(Jar, jar_id)
    if not jar:
        raise HTTPException(status_code=404, detail="Jar not found")

    storage = JarStorage()
    db.delete(jar)
    db.commit()
    storage.delete(jar.name)
    return None


@router.get("/jars/{jar_id}/download")
async def download_jar(jar_id: int, db: Session = Depends(get_db)):
    jar = db.get(Jar, jar_id)
    if not jar:
        raise HTTPException(status_code=404, detail="Jar not found")

    storage = JarStorage()
    if not storage.exists(jar.name):
        raise HTTPException(status_code=410, detail="File missing from storage")

    def iterfile():
        with storage.open(jar.name, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="application/java-archive",
        headers={"Content-Disposition": f"attachment; filename={jar.name}"},
    )
