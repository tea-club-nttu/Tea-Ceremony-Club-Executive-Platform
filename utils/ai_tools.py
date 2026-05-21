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


def fallback_site_usage_guide() -> str:
    return """
第一次使用可以先從「幹部管理」建立幹部名單，讓成果書、行事曆與活動申請書可以直接選擇活動負責人。

接著到「行事曆」新增社課、會議或活動，填入活動名稱、日期、活動負責人、地點與備註。之後在成果書或活動申請書頁面選取行事曆活動，就能自動帶入部分資料，減少重複填寫。

辦完活動後，到「成果書生成」上傳問卷資料與活動照片，確認活動資料後可用 AI 生成活動內容概述與指導老師評語，再下載 Word 成果書。

活動前需要送申請時，到「活動申請書生成」選取或輸入活動資料，可用 AI 產生活動進行與活動宗旨；產生前請檢查流程時間、點心 DIY 與活動內容是否合理。

臨時需要公告、社群貼文、會議紀錄或行政訊息時，可以使用「AI工具」快速產生草稿，再依實際情況修改。幹部常用網站與私密上傳連結則放在「常用連結」。
""".strip()


def generate_site_usage_guide(
    *,
    gemini_api_key: str | None,
    gemini_model: str,
    groq_api_key: str | None,
    groq_model: str,
) -> dict[str, object]:
    fallback_text = fallback_site_usage_guide()

    if not gemini_api_key and not groq_api_key:
        return {
            "text": fallback_text,
            "status": "未設定 API key，已使用本機說明。",
            "provider": "本機說明",
            "model": "",
            "debug": {},
        }

    prompt = """
請替茶道社幹部平台產生首頁使用說明，放在登入後的首頁給幹部閱讀。

平台頁面與用途：
- 幹部管理：建立幹部名單，職位包含社長、副社長、總務、攝錄、點心、文書，活動負責人只需要姓名。
- 行事曆：以月曆管理活動，可填日期、活動名稱、活動負責人、地點與備註。
- 成果書生成：可從行事曆帶入活動資料，上傳問卷與照片，使用 AI 生成活動內容概述與指導老師評語，最後下載 Word。
- 活動申請書生成：可從行事曆與幹部名單帶入資料，使用 AI 產生活動進行與活動宗旨，並提醒使用者檢查流程是否合理。
- 問卷分析：匯入問卷資料並檢視分析結果。
- AI工具：產生活動公告、社群貼文、成果摘要、會議紀錄整理與行政訊息。
- 常用連結：整理幹部常用網站，私密雲端上傳網址由 Streamlit Secrets 載入，不寫入 GitHub。

要求：
- 使用繁體中文。
- 用 5 段以內說明，新幹部看完要知道先做什麼、後做什麼。
- 語氣清楚、親切、像幹部交接文件，不要像廣告。
- 不要提到程式碼、repo、GitHub token 或內部實作。
- 不要使用條列符號，直接用自然段落。
""".strip()

    try:
        result = generate_ai_result(
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
            groq_api_key=groq_api_key,
            groq_model=groq_model,
            system_instruction="你是茶道社幹部平台的使用說明編輯，專門寫清楚、可執行的繁體中文操作指引。",
            prompt=prompt,
        )
    except RuntimeError as exc:
        return {
            "text": fallback_text,
            "status": f"AI 呼叫失敗，已使用本機說明。{exc}",
            "provider": "本機說明",
            "model": "",
            "debug": {},
        }

    return {
        "text": str(result.get("text", "")).strip() or fallback_text,
        "status": f"使用 {result_source(result)} 產生。",
        "provider": result.get("provider", "AI"),
        "model": result.get("model", ""),
        "debug": result.get("debug", {}),
    }


def default_groq_model() -> str:
    return DEFAULT_GROQ_MODEL
