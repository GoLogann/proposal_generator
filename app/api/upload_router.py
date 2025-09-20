import uuid, os
from fastapi import APIRouter, UploadFile, File
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = os.path.join(settings.STORAGE_BASE_PATH, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/uploads")
async def upload_assessment(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[-1].lower()
    path = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")

    with open(path, "wb") as f:
        f.write(await file.read())

    return {"doc_id": doc_id, "filename": file.filename, "path": path}
