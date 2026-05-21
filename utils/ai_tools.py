from __future__ import annotations

from utils.teacher_comment import DEFAULT_GROQ_MODEL, generate_ai_result, result_source


AI_TOOL_TYPES = [
    "活動公告",
    "社群貼文",
    "成果摘要",
    "會議紀錄整理",
    "行政訊息",
]

TOOL_REQUIREMENTS = {
    "活動公告": (
        "請輸出可直接貼到社團群組的活動公告，包含標題、活動資訊、活動內容、"
        "注意事項與一句提醒。語氣清楚親切，不要過度浮誇。"
    ),
    "社群貼文": (
        "請輸出適合 Instagram 或 Facebook 的社群貼文，包含一段主文與 3 到 6 個相關標籤。"
        "語氣活潑但仍符合學校社團形象，不要使用過多 emoji。"
    ),
    "成果摘要": (
        "請輸出適合放入成果紀錄或回報訊息的摘要，內容要具體描述活動做了什麼、"
        "參與者完成什麼，以及可以延伸追蹤的重點。"
    ),
    "會議紀錄整理": (
        "請將原始紀錄整理成正式會議紀錄，包含會議重點、決議事項、待辦事項、"
        "負責人與下次確認事項。若資料沒有負責人，不要自行捏造。"
    ),
    "行政訊息": (
        "請輸出可傳給幹部或社員的行政訊息，包含目的、需要對方完成的事項、期限或提醒。"
        "語氣禮貌、明確、好執行。"
    ),
}


def build_ai_tool_prompt(
    *,
    tool_type: str,
    material: str,
    activity_name: str,
    target: str,
    tone: str,
    length: str,
) -> str:
    requirement = TOOL_REQUIREMENTS.get(tool_type, TOOL_REQUIREMENTS["行政訊息"])
    return f"""
請根據以下資料產生茶道社幹部可使用的文字。

工具類型：{tool_type}
活動或主題名稱：{activity_name or "未填"}
使用對象：{target}
語氣：{tone}
篇幅：{length}

寫作任務：
{requirement}

共同要求：
- 使用繁體中文。
- 內容要能直接複製使用。
- 不要捏造未提供的日期、地點、費用、姓名或活動細節。
- 如果資料不足，請以「可補上：」標示需要人工補充的資訊。
- 不要輸出前言或解釋，不要說「以下是」。
- 避免空泛套話，例如「豐富多元」、「收穫良多」、「圓滿成功」。

輸入素材：
{material or "未提供"}
""".strip()


def fallback_ai_tool_content(
    *,
    tool_type: str,
    material: str,
    activity_name: str,
    target: str,
    tone: str,
    length: str,
) -> str:
    title = activity_name.strip() or "茶道社活動"
    body = material.strip() or "可補上：活動時間、地點、流程、注意事項。"

    if tool_type == "活動公告":
        return (
            f"【{title}】\n"
            f"各位{target}好，茶道社將辦理「{title}」。\n\n"
            f"活動重點：\n{body}\n\n"
            "請大家留意活動時間、地點與需攜帶物品；若有不克參與或需要協助的情況，請提前告知幹部。"
        )

    if tool_type == "社群貼文":
        return (
            f"{title}紀錄\n\n"
            f"{body}\n\n"
            "透過這次活動，我們一起認識茶道流程，也在實作中累積社課經驗。\n\n"
            "#茶道社 #社團活動 #茶文化 #社課紀錄"
        )

    if tool_type == "成果摘要":
        return (
            f"{title}以茶道學習與社課交流為主軸，活動內容包含：{body}。"
            "後續可依參與情形與幹部檢討，補充活動成效與需要調整的流程。"
        )

    if tool_type == "會議紀錄整理":
        return (
            f"{title}會議紀錄\n\n"
            f"一、會議重點\n{body}\n\n"
            "二、決議事項\n可補上：本次會議確認的事項。\n\n"
            "三、待辦事項\n可補上：待辦內容、負責人與期限。\n\n"
            "四、下次確認\n可補上：下次需要追蹤的項目。"
        )

    return (
        f"各位{target}好，關於「{title}」有以下事項需要協助確認：\n\n"
        f"{body}\n\n"
        "請依照訊息內容協助完成，若有問題請提前告知，方便幹部後續統整。"
    )


def generate_ai_tool_content(
    *,
    gemini_api_key: str | None,
    gemini_model: str,
    groq_api_key: str | None,
    groq_model: str,
    tool_type: str,
    material: str,
    activity_name: str,
    target: str,
    tone: str,
    length: str,
) -> dict[str, object]:
    if not gemini_api_key and not groq_api_key:
        return {
            "text": fallback_ai_tool_content(
                tool_type=tool_type,
                material=material,
                activity_name=activity_name,
                target=target,
                tone=tone,
                length=length,
            ),
            "status": "未設定 API key，已使用本機草稿。",
            "provider": "本機草稿",
            "model": "",
            "debug": {},
        }

    prompt = build_ai_tool_prompt(
        tool_type=tool_type,
        material=material,
        activity_name=activity_name,
        target=target,
        tone=tone,
        length=length,
    )
    system_instruction = "你是茶道社幹部的行政文字助手，專門產生可直接使用的繁體中文社團文案。"

    try:
        result = generate_ai_result(
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            groq_api_key=groq_api_key,
            groq_model=groq_model,
            system_instruction=system_instruction,
            prompt=prompt,
        )
    except RuntimeError as exc:
        return {
            "text": fallback_ai_tool_content(
                tool_type=tool_type,
                material=material,
                activity_name=activity_name,
                target=target,
                tone=tone,
                length=length,
            ),
            "status": f"AI 呼叫失敗，已使用本機草稿。{exc}",
            "provider": "本機草稿",
            "model": "",
            "debug": {},
        }

    return {
        "text": str(result.get("text", "")).strip(),
        "status": f"使用 {result_source(result)} 產生。",
        "provider": result.get("provider", "AI"),
        "model": result.get("model", ""),
        "debug": result.get("debug", {}),
    }


def default_groq_model() -> str:
    return DEFAULT_GROQ_MODEL
