from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

from document_engine import DocumentEngine

app = FastAPI(title="Trang Sửa Giáo Án Backend", version="0.1.0")
engine = DocumentEngine()

ALLOWED = {".docx"}

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "document-engine", "export": "disabled-until-validation"}

@app.post("/inspect")
async def inspect(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(status_code=400, detail="Chỉ nhận DOCX ở prototype hiện tại.")
    with TemporaryDirectory() as td:
        src = Path(td) / "source.docx"
        out = Path(td) / "normalized.docx"
        src.write_bytes(await file.read())
        try:
            result = engine.format_document(src, out)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Không thể xử lý DOCX: {exc}") from exc
        # Prototype returns validation metadata; production API will add Change Set/AI review.
        return result

@app.post("/format")
async def format_doc(file: UploadFile = File(...)) -> FileResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(status_code=400, detail="Chỉ nhận DOCX ở prototype hiện tại.")
    with TemporaryDirectory() as td:
        src = Path(td) / "source.docx"
        out = Path(td) / "normalized.docx"
        src.write_bytes(await file.read())
        result = engine.format_document(src, out)
        if not result["export_allowed"]:
            raise HTTPException(status_code=422, detail=result["validation"])
        # FileResponse needs a persistent path, so this endpoint is intentionally not used for deployment yet.
        raise HTTPException(status_code=501, detail="Export persistence chưa bật trong prototype.")
