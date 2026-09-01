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
    """Whole-DOCX inspection. Detects exact phrases and common Vietnamese locality variants."""

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
        return re.sub(r"\s+", " ", (text or "").replace("–", "-").replace("—", "-")).strip().casefold()

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [x for x in re.split(r"[^0-9A-Za-zÀ-ỹĐđ]+", text or "") if len(x) >= 2]

    def _rule_context_ok(self, rule: dict[str, Any], metadata: dict[str, str]) -> bool:
        supplied_subject = self._norm(metadata.get("subject", ""))
        supplied_lesson = self._norm(metadata.get("lesson", ""))
        aliases = {
            "đạo đức": "dao_duc", "lịch sử - địa lí": "lich_su_dia_li", "lịch sử–địa lí": "lich_su_dia_li",
            "lịch sử - địa lý": "lich_su_dia_li", "lịch sử-địa lý": "lich_su_dia_li",
            "toán": "toan", "tiếng việt": "tieng_viet", "khoa học": "khoa_hoc",
        }
        if supplied_subject and aliases.get(supplied_subject, supplied_subject) != str(rule.get("subject", "")):
            return False
        rule_lesson = self._norm(rule.get("lesson", ""))
        if supplied_lesson and rule_lesson and rule_lesson not in supplied_lesson and supplied_lesson not in rule_lesson:
            return False
        return True

    def _variant_pattern(self, old: str) -> str | None:
        """Build a bounded pattern from landmark + legacy locality.

        Example: 'Cột cờ Lũng Cú (Hà Giang)' matches
        'Cột cờ Lũng Cú ở tỉnh Hà Giang'.
        """
        ot = self._tokens(old)
        if len(ot) < 2:
            return None
        province_markers = {"tỉnh", "thành", "phố", "huyện", "xã", "thị", "trấn"}
        stop = province_markers | {"ở", "tại", "thuộc", "là", "một", "góc", "của"}
        # Usually the final 1–4 meaningful tokens form the legacy locality.
        place_len = min(4, max(1, len(ot) // 2))
        place = ot[-place_len:]
        while len(place) > 1 and place[0] in province_markers:
            place = place[1:]
        landmark = [x for x in ot[:-len(place)] if x not in stop]
        if len(landmark) < 1:
            landmark = ot[:-len(place)] or ot[:1]
        p1 = r"\s*[^\n.;:]{0,90}?\s*".join(re.escape(x) for x in landmark[:6])
        p2 = r"\s*(?:ở|tại|thuộc|nằm|là|khu|địa điểm)?\s*(?:(?:tỉnh|thành phố|huyện|xã|thị trấn)\s*)?"
        place_re = r"\s*".join(re.escape(x) for x in place)
        return rf"(?i){p1}{p2}{place_re}"

    def _find_occurrences(self, full_text: str, rule: dict[str, Any]) -> list[tuple[str, str]]:
        old = str(rule.get("old", "")).strip()
        if not old:
            return []
        hay = self._norm(full_text)
        old_n = self._norm(old)
        exact = [(m.group(0), "exact") for m in re.finditer(re.escape(old_n), hay, flags=re.I)]
        if exact:
            return exact
        pat = self._variant_pattern(old)
        if not pat:
            return []
        out: list[tuple[str, str]] = []
        for m in re.finditer(pat, hay, flags=re.I):
            text = m.group(0).strip()
            # Prevent overmatching: the span must contain at least one distinctive legacy-place token.
            legacy = self._tokens(old)[-min(4, len(self._tokens(old))):]
            if any(x in text.casefold() for x in legacy):
                out.append((text, "variant"))
        seen = set(); result=[]
        for x in out:
            if x[0] not in seen:
                seen.add(x[0]); result.append(x)
        return result

    def _curriculum_changes(self, full_text: str, metadata: dict[str, str]) -> list[ChangeSet]:
        out=[]
        for row in self.rules:
            if not self._rule_context_ok(row, metadata):
                continue
            found=self._find_occurrences(full_text, row)
            if not found:
                continue
            action=row.get("action", "review")
            safe=action in {"replace", "replace_contextual", "remove_legacy_district", "remove_legacy_province"}
            for idx,(matched,mode) in enumerate(found,1):
                cid=row["id"] if len(found)==1 else f"{row['id']}#{idx}"
                out.append(ChangeSet(cid,"Curriculum Adjustment Engine","PROPOSED" if safe else "REVIEW_REQUIRED","INFO" if safe else "WARNING",f"{row.get('lesson','')}; {row.get('location','')}".strip("; "),matched,str(row.get("new","")),str(row.get("note","Đối chiếu danh mục điều chỉnh SGK Kết nối tri thức 2026–2027.")) + (" Phát hiện theo biến thể diễn đạt tự nhiên." if mode=="variant" else ""),0.985 if mode=="exact" else 0.97,f"curriculum-adjustments-2026-2027.json#{row['id']}"))
        return out

    def _administrative_changes(self, full_text: str) -> list[ChangeSet]:
        out=[]; hay=self._norm(full_text)
        checks=[
            ("ADMIN-63",r"\b63\s+tỉnh\s*,?\s*thành\s+phố\s+trực\s+thuộc\s+trung\s+ương\b","34 đơn vị hành chính cấp tỉnh, gồm 27 tỉnh và 7 thành phố trực thuộc Trung ương"),
            ("ADMIN-63-BASIC",r"\b63\s+tỉnh\b","34 đơn vị hành chính cấp tỉnh, gồm 27 tỉnh và 7 thành phố trực thuộc Trung ương"),
            ("ADMIN-28-6",r"\b28\s+tỉnh\s*(?:và|\+)\s*6\s+thành\s+phố\b","27 tỉnh + 7 thành phố trực thuộc Trung ương"),
            ("ADMIN-5",r"\b5\s+thành\s+phố\s+trực\s+thuộc\s+trung\s+ương\b","7 thành phố trực thuộc Trung ương"),
        ]
        for cid,pattern,new in checks:
            matches=list(re.finditer(pattern,hay,flags=re.I))
            for idx,m in enumerate(matches,1):
                out.append(ChangeSet(cid if len(matches)==1 else f"{cid}#{idx}","Administrative Data Engine","PROPOSED","WARNING","Toàn văn tài liệu",m.group(0),new,"Phát hiện dữ liệu hành chính cũ; cần cập nhật theo chuẩn 2026–2027.",0.995,f"administrative-standard-2026-2027.json#{cid}"))
        return out

    def _zone_changes(self, full_text: str) -> list[ChangeSet]:
        out=[]; hay=self._norm(full_text)
        rows=self.zones.get("zones",[]) if isinstance(self.zones,dict) else []
        for row in rows:
            name=str(row.get("name") or row.get("zone") or "").strip()
            if not name: continue
            pattern=rf"\bhuyện\s+{re.escape(self._norm(name))}\b"
            matches=list(re.finditer(pattern,hay,flags=re.I))
            for idx,m in enumerate(matches,1):
                cid=f"ZONE-{self._norm(name).replace(' ','-').upper()}"
                out.append(ChangeSet(cid if len(matches)==1 else f"{cid}#{idx}","Special Administrative Zone Engine","REVIEW_REQUIRED","WARNING","Toàn văn tài liệu",m.group(0),f"đặc khu {name}",f"Kiểm tra cách gọi đơn vị hành chính hiện hành của đặc khu {name}; không sửa tự động khi chưa đủ ngữ cảnh.",0.96,f"special-administrative-zones-2026-2027.json#{name}"))
        return out

    def inspect(self,path:Path,metadata:dict[str,str]|None=None)->dict[str,Any]:
        metadata=metadata or {}; doc=Document(str(path)); parts=[p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows: parts.extend(cell.text for cell in row.cells)
        for section in doc.sections:
            parts.extend(p.text for p in section.header.paragraphs); parts.extend(p.text for p in section.footer.paragraphs)
        full_text="\n".join(x for x in parts if x.strip())
        changes=self._curriculum_changes(full_text,metadata)+self._administrative_changes(full_text)+self._zone_changes(full_text)
        return {"document":path.name,"snapshot":{"paragraphs":len(doc.paragraphs),"tables":len(doc.tables),"sections":len(doc.sections),"inlineShapes":len(doc.inline_shapes)},"context":metadata,"changes":[asdict(x) for x in changes],"changeCount":len(changes),"exportAllowed":False,"message":"Đã quét toàn bộ nội dung DOCX khả dụng, gồm đoạn văn, bảng, header/footer và nhận diện biến thể địa danh; chưa sửa file gốc."}

__all__=["ChangeSetEngine","ChangeSet"]
