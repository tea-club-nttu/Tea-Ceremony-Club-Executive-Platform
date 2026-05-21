from __future__ import annotations

import json
from pathlib import Path

from utils.github_json_store import github_token, load_json, save_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LINKS_PATH = DATA_DIR / "useful_links.json"
GITHUB_DATA_PATH = "data/useful_links.json"

DEFAULT_LINKS = [
    {
        "名稱": "課外組空間借用",
        "網址": "https://wdsa.nttu.edu.tw/p/412-1009-8099.php?Lang=zh-tw",
        "分類": "學校網站",
        "備註": "課外活動組空間借用資訊、申請表與場地規定。",
    }
]


def normalize_url(url: str) -> str:
    text = url.strip()
    if text and not text.startswith(("http://", "https://")):
        return f"https://{text}"
    return text


def normalize_links(data: object) -> list[dict[str, str]]:
    if not isinstance(data, list):
        return []

    links = []
    for item in data:
        if not isinstance(item, dict):
            continue

        name = str(item.get("名稱", "")).strip()
        url = normalize_url(str(item.get("網址", "")))
        category = str(item.get("分類", "")).strip()
        note = str(item.get("備註", "")).strip()

        if name and url:
            links.append(
                {
                    "名稱": name,
                    "網址": url,
                    "分類": category,
                    "備註": note,
                }
            )

    return links


def load_links() -> list[dict[str, str]]:
    if github_token():
        remote_links = load_json(GITHUB_DATA_PATH)
        if remote_links is not None:
            return normalize_links(remote_links)

    if not LINKS_PATH.exists():
        return DEFAULT_LINKS

    try:
        data = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_LINKS

    return normalize_links(data)


def save_links(links: list[dict[str, str]]) -> None:
    links = normalize_links(links)

    if github_token() and save_json(GITHUB_DATA_PATH, links, "Update useful links"):
        return

    DATA_DIR.mkdir(exist_ok=True)
    LINKS_PATH.write_text(
        json.dumps(links, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_link(*, name: str, url: str, category: str, note: str) -> None:
    links = load_links()
    links.append(
        {
            "名稱": name.strip(),
            "網址": normalize_url(url),
            "分類": category.strip(),
            "備註": note.strip(),
        }
    )
    save_links(links)


def delete_link(index: int) -> None:
    links = load_links()
    if 0 <= index < len(links):
        del links[index]
        save_links(links)


def move_link(index: int, direction: int) -> None:
    links = load_links()
    new_index = index + direction

    if not 0 <= index < len(links):
        return

    if not 0 <= new_index < len(links):
        return

    links[index], links[new_index] = links[new_index], links[index]
    save_links(links)
