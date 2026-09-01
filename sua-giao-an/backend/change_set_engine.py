from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "master-adjustments-2026-2027.json"
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
    """Whole-DOCX inspection driven by the single master adjustment dataset."""

    def __init__(self) -> None:
        master = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
        self.rules = list(master.get("rules", []))
        if len(self.rules) < 32:
            raise RuntimeError("Master adjustment dataset thiếu quy tắc.")
        self.admin = json.loads(ADMIN_PATH.read_text(encoding="utf-8"))
        self.zones = json.loads(ZONE_PATH.read_text(encoding="utf-8")) if ZONE_PATH.exists() else {}

    @staticmethod
    def _norm(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").replace("–", "-").replace("—", "-")).strip().casefold()

    @classmethod
    def _flex(cls, text: str) -> str:
        return r"\s+".join(re.escape(x) for x in cls._norm(text).split() if x)

    def _context_ok(self, rule: dict[str, Any], metadata: dict[str, str]) -> bool:
        subject = self._norm(metadata.get("subject", ""))
        lesson = self._norm(metadata.get("lesson", ""))
        aliases = {"đạo đức":"DAO_DUC","lịch sử - địa lí":"LICH_SU_DIA_LI","lịch sử–địa lí":"LICH_SU_DIA_LI","lịch sử - địa lý":"LICH_SU_DIA_LI","lịch sử-địa lý":"LICH_SU_DIA_LI","toán":"TOAN","tiếng việt":"TIENG_VIET","khoa học":"KHOA_HOC"}
        if subject and aliases.get(subject, subject) != str(rule.get("subject", "")):
            return False
        rl = self._norm(rule.get("lesson", ""))
        return not (lesson and rl and lesson not in rl and rl not in lesson)

    def _find_occurrences(self, text: str, rule: dict[str, Any]) -> list[str]:
        found: list[str] = []
        for phrase in [rule.get("old", ""), *(rule.get("patterns", []) or [])]:
            phrase = str(phrase).strip()
            if not phrase:
                continue
            rx = re.compile(self._flex(phrase), re.I)
            for m in rx.finditer(text):
                if m.group(0) not in found:
                    found.append(m.group(0))
        return found

    def inspect(self, path: Path, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        metadata = metadata or {}
        doc = Document(str(path))
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.extend(cell.text for cell in row.cells)
        for section in doc.sections:
            parts.extend(p.text for p in section.header.paragraphs)
            parts.extend(p.text for p in section.footer.paragraphs)
        text = "\n".join(x for x in parts if x.strip())
        changes: list[ChangeSet] = []
        for rule in self.rules:
            if not self._context_ok(rule, metadata):
                continue
            for matched in self._find_occurrences(text, rule):
                review = rule.get("action") == "review_image"
                changes.append(ChangeSet(rule["id"],"Master Adjustment Engine","REVIEW_REQUIRED" if review else "PROPOSED","WARNING" if review else "INFO",f"{rule.get('lesson','')}; {rule.get('location','')}".strip("; "),matched,str(rule.get("new", "")),str(rule.get("reason", "Đối chiếu Master Adjustment Dataset 2026–2027.")),0.99,f"master-adjustments-2026-2027.json#{rule['id']}"))
        for cid,pattern,new in [("ADMIN-63",r"63\s+tỉnh\s*(?:,\s*)?(?:và\s*)?thành\s+phố","34 đơn vị hành chính cấp tỉnh, gồm 27 tỉnh và 7 thành phố trực thuộc Trung ương"),("ADMIN-28-6",r"28\s+tỉnh\s*(?:và|\+)\s*6\s+thành\s+phố","27 tỉnh và 7 thành phố trực thuộc Trung ương"),("ADMIN-5",r"5\s+thành\s+phố\s+trực\s+thuộc\s+Trung\s+ương","7 thành phố trực thuộc Trung ương")]:
            for idx,m in enumerate(re.finditer(pattern,text,re.I),1):
                changes.append(ChangeSet(f"{cid}#{idx}","Administrative Data Engine","PROPOSED","WARNING","Toàn văn",m.group(0),new,"Dữ liệu hành chính cũ; cập nhật theo chuẩn hiện hành 2026.",0.995,f"administrative-standard-2026-2027.json#{cid}"))
        return {"document":path.name,"snapshot":{"paragraphs":len(doc.paragraphs),"tables":len(doc.tables),"sections":len(doc.sections),"inlineShapes":len(doc.inline_shapes)},"context":metadata,"changes":[asdict(x) for x in changes],"changeCount":len(changes),"exportAllowed":False,"message":"Master Whole-DOCX scan completed; source file not mutated."}

__all__=["ChangeSetEngine","ChangeSet"]
