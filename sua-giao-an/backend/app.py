from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

from change_set_engine import ChangeSetEngine

app = FastAPI(title="Trang Sửa Giáo Án Backend", version="0.3.0")
engine = ChangeSetEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

ALLOWED = {".docx"}

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "document-engine",
        "version": "0.3.0",
        "curriculum_engine": True,
        "administrative_engine": True,
        "special_zone_engine": True,
        "change_set_engine": True,
        "mutation": False,
        "export": "disabled-until-approval-and-validation",
    }

@app.post("/inspect")
async def inspect(
    file: UploadFile = File(...),
    subject: str = Form(""),
    lesson: str = Form(""),
    location: str = Form("Toàn văn"),
    school_year: str = Form("2026-2027"),
) -> dict:
    filename = file.filename or ""
    if Path(filename).suffix.lower() not in ALLOWED:
        raise HTTPException(status_code=400, detail="Prototype hiện chỉ nhận tệp DOCX.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Tệp rỗng.")

    tmp_path: Path | None = None
    try:
        with NamedTemporaryFile(prefix="lesson-inspect-", suffix=".docx", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        result = engine.inspect(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Không thể phân tích DOCX: {exc}") from exc
    finally:
        if tmp_path:
            tmp_path.unlink(missing_ok=True)

    result["metadata"] = {
        "subject": subject.strip(),
        "lesson": lesson.strip(),
        "location": location.strip() or "Toàn văn",
        "school_year": school_year.strip() or "2026-2027",
    }
    result["analysis_only"] = True
    result["mutation_performed"] = False
    result["next_step"] = "review_change_sets"
    return result

@app.post("/format")
async def format_doc(file: UploadFile = File(...)) -> dict:
    raise HTTPException(
        status_code=409,
        detail="Chưa cho phép sửa/xuất tự động. Phải qua Change Set → duyệt → Document Engine → Format Engine → Validator.",
    )
