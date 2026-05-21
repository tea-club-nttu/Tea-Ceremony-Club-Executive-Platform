import streamlit as st

from utils.auth import init_auth_state, logout_button
from utils.ai_tools import (
    default_groq_model,
    fallback_site_usage_guide,
    generate_site_usage_guide,
)


def secret_value(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


st.set_page_config(
    page_title="茶道社幹部平台",
    page_icon="🍵",
    layout="wide",
)

init_auth_state()

st.title("茶道社幹部平台")
st.caption("社團幹部日常作業入口")

with st.sidebar:
    st.header("茶道社幹部平台")
    if st.session_state["authenticated"]:
        st.success("已登入")
        logout_button()
    else:
        st.info("請先登入後使用功能頁面")


if st.session_state["authenticated"]:
    st.success("登入成功，請從左側 sidebar 選擇功能頁面。")

    st.subheader("平台功能")
    col1, col2 = st.columns(2)

    with col1:
        st.info("成果書生成\n\n整理活動資料並產生成果書文件。")
        st.info("活動申請書生成\n\n帶入活動資料並產生申請計畫書。")
        st.info("問卷分析\n\n匯入問卷資料並檢視分析結果。")

    with col2:
        st.info("AI工具\n\n提供幹部行政與文案輔助工具。")
        st.info("幹部管理\n\n維護幹部資料與職位分工。")
        st.info("行事曆\n\n記錄社課、會議與活動時程。")
        st.info("常用連結\n\n整理幹部常用網站並快速跳轉。")

    st.subheader("AI 使用說明")
    st.caption("登入後可在這裡查看平台操作指引，需要時再用 AI 更新成更自然的說明。")

    if "site_usage_guide_result" not in st.session_state:
        st.session_state["site_usage_guide_result"] = {
            "text": fallback_site_usage_guide(),
            "status": "目前顯示本機說明，可按下方按鈕用 AI 更新。",
            "provider": "本機說明",
            "model": "",
            "debug": {},
        }

    guide_result = st.session_state["site_usage_guide_result"]
    st.info(str(guide_result.get("status", "")))
    st.markdown(str(guide_result.get("text", "")))

    guide_col1, guide_col2 = st.columns([1, 4])
    with guide_col1:
        if st.button("用 AI 更新說明", type="primary"):
            with st.spinner("正在用 AI 產生網站使用說明..."):
                st.session_state["site_usage_guide_result"] = generate_site_usage_guide(
                    gemini_api_key=secret_value("GEMINI_API_KEY"),
                    gemini_model=secret_value("GEMINI_MODEL", "gemini-2.5-flash"),
                    groq_api_key=secret_value("GROQ_API_KEY"),
                    groq_model=secret_value("GROQ_MODEL", default_groq_model()),
                )
            st.rerun()
    with guide_col2:
        provider = guide_result.get("provider")
        model = guide_result.get("model")
        if provider and provider != "本機說明":
            st.caption(f"調用模型：{provider} / {model}")
        else:
            st.caption("AI 說明會根據目前平台功能產生，產出後仍可依幹部實際流程調整。")
else:
    st.subheader("登入")
    password = st.text_input("請輸入平台密碼", type="password")

    if st.button("登入", type="primary"):
        if password == st.secrets["PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("密碼錯誤，請再試一次。")
