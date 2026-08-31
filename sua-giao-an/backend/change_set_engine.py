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
    """Deterministic DOCX inspection. Creates proposals only; never mutates the source."""

    def __init__(self) -> None:
        self.curriculum = json.loads(CURRICULUM_PATH.read_text(encoding="utf-8"))
        self.admin = json.loads(ADMIN_PATH.read_text(encoding="utf-8"))
        self.zones = json.loads(ZONE_PATH.read_text(encoding="utf-8")) if ZONE_PATH.exists() else {}
        self.rules: list[dict[str, Any]] = []
        for subject, rows in self.curriculum.get("subjects", {}).items():
            for row in rows:
                item = dict(row)
                item["subject"] = subject
                self.rules.append(item)

    @staticmethod
    def _norm(text: str) -> str:
        text = (text or "").replace("–", "-").replace("—", "-")
        return re.sub(r"\s+", " ", text).strip().casefold()

    def _rule_context_ok(self, rule: dict[str, Any], metadata: dict[str, str]) -> bool:
        supplied_subject = self._norm(metadata.get("subject", ""))
        supplied_lesson = self._norm(metadata.get("lesson", ""))
        supplied_location = self._norm(metadata.get("location", ""))
        aliases = {
            "đạo đức": "DAO_DUC", "lịch sử - địa lí": "LICH_SU_DIA_LI", "lịch sử–địa lí": "LICH_SU_DIA_LI",
            "toán": "TOAN", "tiếng việt": "TIENG_VIET", "khoa học": "KHOA_HOC",
        }
        rule_subject = self._norm(rule.get("subject", ""))
        if supplied_subject and rule_subject in aliases:
            if aliases[supplied_subject] != rule_subject:
                return False
        elif supplied_subject and supplied_subject != rule_subject:
            return False

        rule_lesson = self._norm(rule.get("lesson", ""))
        if supplied_lesson and rule_lesson:
            # Exact or containment match for values such as "Bài 11" / "Bài 11 trang 56".
            if rule_lesson not in supplied_lesson and supplied_lesson not in rule_lesson:
                return False

        rule_location = self._norm(rule.get("location", ""))
        if supplied_location and supplied_location != "toàn văn" and rule_location:
            if rule_location not in supplied_location and supplied_location not in rule_location:
                # Page/figure can still be found in the document text; don't reject yet.
                pass
        return True

    def _find_context(self, full_text: str, rule: dict[str, Any]) -> bool:
        old = self._norm(rule.get("old", ""))
        hay = self._norm(full_text)
        if not old:
            return False
        if old in hay:
            return True
        tokens = [re.escape(x) for x in re.split(r"[\s,;()]+", old) if x]
        if len(tokens) >= 3:
            pattern = r"\s*".join(tokens[: min(len(tokens), 16)])
            return re.search(pattern, hay, flags=re.I) is not None
        return False

    def _curriculum_changes(self, full_text: str, metadata: dict[str, str]) -> list[ChangeSet]:
        out: list[ChangeSet] = []
        for row in self.rules:
            if self._rule_context_ok(row, metadata) and self._find_context(full_text, row):
                action = row.get("action", "review")
                out.append(ChangeSet(
                    id=row["id"],
                    engine="Curriculum Adjustment Engine",
                    status="PROPOSED" if action not in {"flag_and_propose", "replace_or_flag_image"} else "REVIEW_REQUIRED",
                    severity="WARNING" if action in {"flag_and_propose", "replace_or_flag_image"} else "INFO",
                    location=f"{row.get('lesson','')}; {row.get('location','')}".strip("; "),
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

        m = re.search(r"tỉnh\s+Đồng\s+Nai", full_text, flags=re.I)
        if m:
            out.append(ChangeSet("ADMIN-DONGNAI", "Administrative Data Engine", "REVIEW_REQUIRED", "WARNING", "Toàn văn tài liệu", m.group(0), "Thành phố Đồng Nai", "Từ 30/04/2026, Đồng Nai là thành phố trực thuộc Trung ương; cần đối chiếu ngữ cảnh và thời điểm văn bản.", 0.98, "administrative-standard-2026-2027.json#dongNai"))
        return out

    def _zone_changes(self, full_text: str) -> list[ChangeSet]:
        out: list[ChangeSet] = []
        rows = self.zones.get("zones", []) if isinstance(self.zones, dict) else []
        for row in rows:
            name = row.get("name") or row.get("zone") or ""
            if not name:
                continue
            pattern = rf"huyện\s+{re.escape(name)}"
            m = re.search(pattern, full_text, flags=re.I)
            if m:
                slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()
                out.append(ChangeSet(
                    id=f"ZONE-{slug}", engine="Special Administrative Zone Engine", status="REVIEW_REQUIRED", severity="WARNING",
                    location="Toàn văn tài liệu", old=m.group(0), new=f"đặc khu {name}",
                    reason=f"Kiểm tra cách gọi đơn vị hành chính hiện hành của đặc khu {name}; không sửa tự động nếu chưa xác định ngữ cảnh.",
                    confidence=0.96, source_ref=f"special-administrative-zones-2026-2027.json#{name}",
                ))
        return out

    def inspect(self, path: Path, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        metadata = metadata or {}
        doc = Document(str(path))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.extend(cell.text for cell in row.cells)
        full_text = "\n".join(x for x in parts if x.strip())
        changes = self._curriculum_changes(full_text, metadata) + self._administrative_changes(full_text) + self._zone_changes(full_text)
        return {
            "document": path.name,
            "snapshot": {"paragraphs": len(doc.paragraphs), "tables": len(doc.tables), "sections": len(doc.sections), "inlineShapes": len(doc.inline_shapes)},
            "context": metadata,
            "changes": [asdict(x) for x in changes],
            "changeCount": len(changes),
            "exportAllowed": False,
            "message": "Đã phân tích và tạo Change Set; chưa sửa file gốc.",
        }

__all__ = ["ChangeSetEngine", "ChangeSet"]
