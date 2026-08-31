from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM_PATH = ROOT / "curriculum-adjustments-2026-2027.json"
ADMIN_PATH = ROOT / "administrative-standard-2026-2027.json"
ZONE_PATH = ROOT / "special-administrative-zones-2026-2027.json"


@dataclass
class ChangeSet:
    id: str
    engine: str
    status: str
    severity: str
    location: str
    old: str
    new: str
    reason: str
    confidence: float
    source_ref: str


class ChangeSetEngine:
    """Inspect a DOCX and create reviewable Change Sets without modifying it."""

    def __init__(self) -> None:
        self.curriculum = json.loads(CURRICULUM_PATH.read_text(encoding="utf-8"))
        self.admin = json.loads(ADMIN_PATH.read_text(encoding="utf-8"))
        self.zones = json.loads(ZONE_PATH.read_text(encoding="utf-8")) if ZONE_PATH.exists() else {}
        self.rules: list[dict[str, Any]] = []
        for subject, rows in self.curriculum.get("subjects", {}).items():
            for row in rows:
                row = dict(row)
                row["subject"] = subject
                self.rules.append(row)

    @staticmethod
    def _norm(text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    @staticmethod
    def _find_context(full_text: str, rule: dict[str, Any]) -> bool:
        old = ChangeSetEngine._norm(rule.get("old", ""))
        if not old:
            return False
        hay = ChangeSetEngine._norm(full_text)
        # exact-ish matching first; allow line breaks, multiple spaces and punctuation spacing.
        if old in hay:
            return True
        tokens = [re.escape(x) for x in re.split(r"[\s,;()]+", old) if x]
        if len(tokens) >= 3:
            pattern = r"\s*".join(tokens[: min(len(tokens), 12)])
            return re.search(pattern, hay, flags=re.I) is not None
        return False

    def _curriculum_changes(self, full_text: str) -> list[ChangeSet]:
        out: list[ChangeSet] = []
        for row in self.rules:
            if self._find_context(full_text, row):
                out.append(ChangeSet(
                    id=row["id"],
                    engine="Curriculum Adjustment Engine",
                    status="PROPOSED" if row.get("action") != "flag_and_propose" else "REVIEW_REQUIRED",
                    severity="WARNING" if row.get("action") in {"flag_and_propose", "replace_or_flag_image"} else "INFO",
                    location=f"{row.get('lesson','')}; {row.get('location','')}`".strip("; `"),
                    old=row.get("old", ""),
                    new=row.get("new", ""),
                    reason=row.get("note", "Đối chiếu danh mục điều chỉnh SGK Kết nối tri thức 2026–2027."),
                    confidence=0.99,
                    source_ref=f"curriculum-adjustments-2026-2027.json#{row['id']}",
                ))
        return out

    def _administrative_changes(self, full_text: str) -> list[ChangeSet]:
        out: list[ChangeSet] = []
        checks = [
            ("ADMIN-63", r"63\s+tỉnh(?:,|\s+và)?\s+thành phố", "34 đơn vị hành chính cấp tỉnh, gồm 27 tỉnh và 7 thành phố trực thuộc Trung ương", "Dữ liệu cũ trước chuẩn 2026–2027."),
            ("ADMIN-28-6", r"28\s+tỉnh\s*(?:và|\+)\s*6\s+thành phố", "27 tỉnh + 7 thành phố trực thuộc Trung ương", "Cơ cấu trước khi Đồng Nai trở thành thành phố trực thuộc Trung ương."),
            ("ADMIN-5", r"5\s+thành phố\s+trực\s+thuộc\s+Trung\s+ương", "7 thành phố trực thuộc Trung ương", "Cơ cấu cũ; cần cập nhật theo chuẩn hiện hành."),
        ]
        for cid, pattern, new, reason in checks:
            m = re.search(pattern, full_text, flags=re.I)
            if m:
                out.append(ChangeSet(cid, "Administrative Data Engine", "PROPOSED", "WARNING", "Toàn văn tài liệu", m.group(0), new, reason, 0.99, f"administrative-standard-2026-2027.json#{cid}"))

        # Context-aware Đồng Nai check.
        m = re.search(r"tỉnh\s+Đồng\s+Nai", full_text, flags=re.I)
        if m:
            out.append(ChangeSet("ADMIN-DONGNAI", "Administrative Data Engine", "REVIEW_REQUIRED", "WARNING", "Toàn văn tài liệu", m.group(0), "Thành phố Đồng Nai", "Từ 30/04/2026, Đồng Nai là thành phố trực thuộc Trung ương; cần đối chiếu ngữ cảnh và thời điểm văn bản.", 0.98, "administrative-standard-2026-2027.json#dongNai"))
        return out

    def _zone_changes(self, full_text: str) -> list[ChangeSet]:
        out: list[ChangeSet] = []
        mappings = self.zones.get("zones", self.zones if isinstance(self.zones, dict) else {})
        if isinstance(mappings, list):
            rows = mappings
        else:
            rows = mappings.get("zones", []) if isinstance(mappings, dict) else []
        for row in rows:
            name = row.get("name") or row.get("zone") or ""
            if not name:
                continue
            # Only flag an old district label when the exact combination exists.
            pattern = rf"huyện\s+{re.escape(name)}"
            m = re.search(pattern, full_text, flags=re.I)
            if m:
                out.append(ChangeSet(
                    id=f"ZONE-{re.sub(r'[^A-Za-z0-9]+','-',name).strip('-').upper()}",
                    engine="Special Administrative Zone Engine",
                    status="REVIEW_REQUIRED",
                    severity="WARNING",
                    location="Toàn văn tài liệu",
                    old=m.group(0),
                    new=f"đặc khu {name}",
                    reason=f"Kiểm tra cách gọi đơn vị hành chính hiện hành của đặc khu {name}. Không sửa tự động nếu chưa xác định ngữ cảnh.",
                    confidence=0.96,
                    source_ref=f"special-administrative-zones-2026-2027.json#{name}",
                ))
        return out

    def inspect(self, path: Path) -> dict[str, Any]:
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                paragraphs.extend(cell.text for cell in row.cells)
        full_text = "\n".join(x for x in paragraphs if x.strip())
        changes = self._curriculum_changes(full_text) + self._administrative_changes(full_text) + self._zone_changes(full_text)
        return {
            "document": path.name,
            "snapshot": {
                "paragraphs": len(doc.paragraphs),
                "tables": len(doc.tables),
                "sections": len(doc.sections),
                "inlineShapes": len(doc.inline_shapes),
            },
            "changes": [asdict(x) for x in changes],
            "changeCount": len(changes),
            "exportAllowed": False,
            "message": "Đã phân tích và tạo Change Set; chưa sửa file gốc.",
        }


__all__ = ["ChangeSetEngine", "ChangeSet"]
