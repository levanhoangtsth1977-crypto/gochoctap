from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import FastAPI, File, UploadFile, HTTPException

from curriculum_engine import analyze_docx_bytes

app = FastAPI(title="Trang Sửa Giáo Án Backend", version="0.2.0")

ALLOWED = {".docx"}
KB_ROOT = Path(__file__).resolve().parent.parent


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "document-engine",
        "curriculum_engine": True,
        "administrative_engine": True,
        "special_zone_engine": True,
        "mutation": False,
        "export": "disabled-until-approval-and-validation",
    }


def _metadata_from_filename(filename: str) -> dict[str, str]:
    # Metadata is intentionally conservative. Filename hints never override document content.
    stem = Path(filename).stem if filename else ""
    return {"subject": "", "lesson": stem, "location": "Toàn văn"}


@app.post("/inspect")
async def inspect(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(status_code=400, detail="Chỉ nhận DOCX ở prototype engine hiện tại.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Tệp rỗng.")

    metadata = _metadata_from_filename(filename)
    result = analyze_docx_bytes(data, metadata, KB_ROOT)
    if not result.get("ok"):
        raise HTTPException(status_code=422, detail=result.get("error", "Không thể phân tích DOCX."))

    return {
        "filename": filename,
        "engine_version": "0.2.0",
        "analysis_only": True,
        "document": result["document"],
        "change_sets": result["change_sets"],
        "mutation_performed": False,
        "next_step": "review_change_sets",
    }


@app.post("/format")
async def format_doc(file: UploadFile = File(...)) -> dict:
    raise HTTPException(
        status_code=409,
        detail="Chưa cho phép sửa/xuất tự động. Phải qua Change Set → duyệt → Document Engine → Format Engine → Validator.",
    )
