from __future__ import annotations

import json
from pathlib import Path

from utils.github_json_store import (
    github_token,
    load_json,
    save_json,
    storage_label,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OFFICERS_PATH = DATA_DIR / "officers.json"
OFFICER_ROLES = ["社長", "副社長", "總務", "攝錄", "點心", "文書", "美宣"]
GITHUB_DATA_PATH = "data/officers.json"


def normalize_officers(data: object) -> list[dict[str, str]]:
    if not isinstance(data, list):
        return []

    officers = []
    for item in data:
        if not isinstance(item, dict):
            continue

        name = str(item.get("姓名", "")).strip()
        student_id = str(item.get("學號", "")).strip()
        role = str(item.get("職位", "")).strip()

        if name:
            officers.append({"姓名": name, "學號": student_id, "職位": role})

    return officers


def load_officers() -> list[dict[str, str]]:
    if github_token():
        remote_officers = load_json(GITHUB_DATA_PATH)
        if remote_officers is not None:
            return normalize_officers(remote_officers)

    if not OFFICERS_PATH.exists():
        return []

    try:
        data = json.loads(OFFICERS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    return normalize_officers(data)


def save_officers(officers: list[dict[str, str]]) -> None:
    if github_token() and save_json(GITHUB_DATA_PATH, officers, "Update officer list", strict=True):
        return

    DATA_DIR.mkdir(exist_ok=True)
    OFFICERS_PATH.write_text(
        json.dumps(officers, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def add_officer(*, name: str, student_id: str, role: str) -> None:
    officers = load_officers()
    officers.append(
        {
            "姓名": name.strip(),
            "學號": student_id.strip(),
            "職位": role.strip(),
        }
    )
    save_officers(officers)


def delete_officer(index: int) -> None:
    officers = load_officers()
    if 0 <= index < len(officers):
        del officers[index]
        save_officers(officers)


def move_officer(index: int, direction: int) -> None:
    officers = load_officers()
    new_index = index + direction

    if not 0 <= index < len(officers):
        return

    if not 0 <= new_index < len(officers):
        return

    officers[index], officers[new_index] = officers[new_index], officers[index]
    save_officers(officers)


def move_officer_to_top(index: int) -> None:
    officers = load_officers()

    if not 0 <= index < len(officers):
        return

    officer = officers.pop(index)
    officers.insert(0, officer)
    save_officers(officers)


def format_officer_label(officer: dict[str, str]) -> str:
    name = officer.get("姓名", "")
    role = officer.get("職位", "")
    student_id = officer.get("學號", "")

    details = "、".join(item for item in (role, student_id) if item)
    if details:
        return f"{name}（{details}）"

    return name
