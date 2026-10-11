from __future__ import annotations

import base64
import json
import os
from urllib import error, parse, request


GITHUB_REPO = "tea-club-nttu/Tea-Ceremony-Club-Executive-Platform"
GITHUB_BRANCH = "main"


def get_secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value

    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def github_token() -> str:
    return get_secret("GITHUB_TOKEN")


def github_contents_url(path: str) -> str:
    encoded_path = parse.quote(path)
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/{encoded_path}"


def github_request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def load_json(path: str) -> object | None:
    token = github_token()
    if not token:
        return None

    url = f"{github_contents_url(path)}?ref={parse.quote(GITHUB_BRANCH)}"

    try:
        response = github_request("GET", url, token)
    except (OSError, error.HTTPError, json.JSONDecodeError):
        return None

    content = response.get("content", "")
    if not content:
        return []

    try:
        decoded = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        return None


class StorageError(RuntimeError):
    pass


def storage_failure(exc: Exception, strict: bool) -> bool:
    if strict:
        code = getattr(exc, "code", None)
        reason = {
            401: "金鑰無效或已過期。",
            403: "請確認 Contents 寫入權限、組織核准及 API 額度。",
            404: "找不到專案或金鑰沒有此專案的存取權限。",
            409: "遠端資料已變更，請重新整理後再試。",
            422: "GitHub 拒絕此更新，請檢查分支規則或檔案狀態。",
        }.get(code, "連線失敗或回覆格式異常，請稍後再試。")
        status = f"（HTTP {code}）" if code else ""
        raise StorageError(f"尚未儲存至 GitHub{status}：{reason}") from None
    return False


def save_json(path: str, data: object, message: str, *, strict: bool = False) -> bool:
    token = github_token()
    if not token:
        return False

    url = f"{github_contents_url(path)}?ref={parse.quote(GITHUB_BRANCH)}"
    sha = None

    try:
        current_file = github_request("GET", url, token)
        sha = current_file.get("sha")
    except error.HTTPError as exc:
        if exc.code != 404:
            return storage_failure(exc, strict)
    except (OSError, json.JSONDecodeError) as exc:
        return storage_failure(exc, strict)

    content = json.dumps(data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")
    payload = {
        "message": message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH,
    }

    if sha:
        payload["sha"] = sha

    try:
        github_request("PUT", github_contents_url(path), token, payload)
    except (OSError, error.HTTPError, json.JSONDecodeError) as exc:
        return storage_failure(exc, strict)

    return True


def storage_label() -> str:
    if github_token():
        return "GitHub 儲存（已設定金鑰；以實際寫入結果為準）"

    return "本機檔案儲存"
