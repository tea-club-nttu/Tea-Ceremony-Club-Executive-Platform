import streamlit as st

from utils.auth import init_auth_state, logout_button
from utils.ai_tools import (
    default_groq_model,
    fallback_site_usage_guide,
    generate_site_help_answer,
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
        st.page_link("pages/1_成果書生成.py", label="成果書生成", icon="📄")
        st.caption("整理活動資料並產生成果書文件。")
        st.page_link("pages/6_活動申請書生成.py", label="活動申請書生成", icon="📝")
        st.caption("帶入活動資料並產生申請計畫書。")
        st.page_link("pages/2_問卷分析.py", label="問卷分析", icon="📊")
        st.caption("匯入問卷資料並檢視分析結果。")

    with col2:
        st.page_link("pages/3_AI工具.py", label="AI工具", icon="✨")
        st.caption("提供幹部行政與文案輔助工具。")
        st.page_link("pages/4_幹部管理.py", label="幹部管理", icon="👥")
        st.caption("維護幹部資料與職位分工。")
        st.page_link("pages/5_行事曆.py", label="行事曆", icon="📅")
        st.caption("記錄社課、會議與活動時程。")
        st.page_link("pages/7_常用連結.py", label="常用連結", icon="🔗")
        st.caption("整理幹部常用網站並快速跳轉。")

    st.divider()
    st.subheader("平台說明")

    if "site_usage_guide_result" not in st.session_state:
        st.session_state["site_usage_guide_result"] = {
            "text": fallback_site_usage_guide(),
            "status": "目前顯示簡短本機說明。",
            "provider": "本機說明",
            "model": "",
            "debug": {},
        }

    guide_result = st.session_state["site_usage_guide_result"]
    with st.container(border=True):
        st.caption(str(guide_result.get("text", "")))
        guide_col1, guide_col2 = st.columns([1, 4])
        with guide_col1:
            if st.button("AI 簡介", type="secondary"):
                with st.spinner("正在用 AI 更新平台簡介..."):
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
                st.caption(f"平台簡介模型：{provider} / {model}")
            else:
                st.caption(str(guide_result.get("status", "")))

        st.markdown("**快速跳轉**")
        link_col1, link_col2, link_col3, link_col4 = st.columns(4)
        with link_col1:
            st.page_link("pages/1_成果書生成.py", label="成果書", icon="📄")
            st.page_link("pages/6_活動申請書生成.py", label="申請書", icon="📝")
        with link_col2:
            st.page_link("pages/4_幹部管理.py", label="幹部管理", icon="👥")
            st.page_link("pages/5_行事曆.py", label="行事曆", icon="📅")
        with link_col3:
            st.page_link("pages/3_AI工具.py", label="AI工具", icon="✨")
            st.page_link("pages/2_問卷分析.py", label="問卷分析", icon="📊")
        with link_col4:
            st.page_link("pages/7_常用連結.py", label="常用連結", icon="🔗")

    st.subheader("問 AI 怎麼操作")
    with st.form("site_help_form"):
        help_question = st.text_input(
            "想做什麼？",
            placeholder="例：我要做成果書要去哪裡？我要新增活動負責人怎麼做？",
        )
        help_submitted = st.form_submit_button("詢問 AI", type="primary")

    if help_submitted:
        if not help_question.strip():
            st.error("請先輸入你想問的操作。")
        else:
            with st.spinner("正在用 AI 產生網站使用說明..."):
                st.session_state["site_help_result"] = generate_site_help_answer(
                    gemini_api_key=secret_value("GEMINI_API_KEY"),
                    gemini_model=secret_value("GEMINI_MODEL", "gemini-2.5-flash"),
                    groq_api_key=secret_value("GROQ_API_KEY"),
                    groq_model=secret_value("GROQ_MODEL", default_groq_model()),
                    question=help_question,
                )
            st.rerun()

    help_result = st.session_state.get("site_help_result")
    if help_result:
        st.success(str(help_result.get("status", "已回答。")))
        st.write(str(help_result.get("text", "")))
        provider = help_result.get("provider")
        model = help_result.get("model")
        if provider and provider != "本機回答":
            st.caption(f"調用模型：{provider} / {model}")
else:
    st.subheader("登入")
    password = st.text_input("請輸入平台密碼", type="password")

    if st.button("登入", type="primary"):
        if password == st.secrets["PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("密碼錯誤，請再試一次。")
