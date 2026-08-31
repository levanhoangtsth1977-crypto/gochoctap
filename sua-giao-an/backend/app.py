from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

from change_set_engine import ChangeSetEngine

app = FastAPI(title="Trang Sửa Giáo Án Backend", version="0.3.0")
engine = ChangeSetEngine()

ALLOWED = {".docx"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    tmp = Path("/tmp") / f"lesson-inspect-{Path(filename).name}"
    tmp.write_bytes(data)
    try:
        result = engine.inspect(tmp)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Không thể phân tích DOCX: {exc}") from exc
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass

    # Add explicit metadata to the review payload. Matching remains deterministic.
    result["metadata"] = {
        "subject": subject,
        "lesson": lesson,
        "location": location,
        "school_year": school_year,
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
