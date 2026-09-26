from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document

from utils.achievement_report import replace_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPLICATION_TEMPLATE_PATH = PROJECT_ROOT / "assets" / "活動申請書模板.docx"


def build_application_form(
    *,
    template_file,
    fields: dict[str, object],
) -> BytesIO:
    template_source = (
        template_file
        if template_file is not None
        else str(DEFAULT_APPLICATION_TEMPLATE_PATH)
    )
    doc = Document(template_source)

    replacements = {
        "{{活動名稱}}": str(fields.get("activity_name", "")),
        "{{活動日期}}": str(fields.get("activity_date", "")),
        "{{活動負責人}}": str(fields.get("activity_leader", "")),
        "{{活動副負責人}}": str(fields.get("activity_deputy_leader", "")),
        "{{負責人電話}}": str(fields.get("leader_phone", "")),
        "{{活動宗旨}}": str(fields.get("activity_purpose", "")),
        "{{活動進行}}": str(fields.get("activity_progress", "")),
        "{{點心}}": str(fields.get("snack_item", "")),
        "{{活動流程日期}}": str(fields.get("progress_date", "")),
        "{{流程日期}}": str(fields.get("progress_date", "")),
    }
    for role in ("社長", "副社長", "總務", "攝錄", "點心", "文書"):
        name = str(fields.get("officer_names", {}).get(role, ""))
        replacements[f"{{{{{role}姓名}}}}"] = name
        replacements[f"{{{{{role}名字}}}}"] = name
        if role != "點心":
            replacements[f"{{{{{role}}}}}"] = name

    replace_text(doc, replacements)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output
