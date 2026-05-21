import streamlit as st

from utils.auth import require_login, logout_button
from utils.github_json_store import storage_label
from utils.link_store import add_link, delete_link, load_links, move_link, normalize_url


st.set_page_config(
    page_title="常用連結 | 茶道社幹部平台",
    page_icon="🍵",
    layout="wide",
)

require_login()

with st.sidebar:
    st.success("已登入")
    logout_button()

st.title("常用連結")
st.caption("整理幹部常用網站，點選後可直接跳轉。")
st.caption(f"儲存位置：{storage_label()}")

with st.expander("新增連結", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        link_name = st.text_input("連結名稱")
        link_category = st.text_input("分類", value="學校網站")
    with col2:
        link_url = st.text_input("網址")
        link_note = st.text_input("備註")

    if st.button("新增連結", type="primary"):
        normalized_url = normalize_url(link_url)
        if not link_name.strip():
            st.error("請輸入連結名稱。")
        elif not normalized_url.startswith(("http://", "https://")):
            st.error("請輸入有效網址。")
        else:
            add_link(
                name=link_name,
                url=normalized_url,
                category=link_category,
                note=link_note,
            )
            st.success("已新增連結。")
            st.rerun()

links = load_links()

if not links:
    st.info("目前尚未新增常用連結。")
else:
    categories = []
    for link in links:
        category = link.get("分類", "").strip() or "未分類"
        if category not in categories:
            categories.append(category)

    for category in categories:
        st.subheader(category)
        for index, link in enumerate(links):
            if (link.get("分類", "").strip() or "未分類") != category:
                continue

            with st.container(border=True):
                title_col, action_col = st.columns([4, 1])
                with title_col:
                    st.markdown(f"**{link.get('名稱', '')}**")
                    if link.get("備註"):
                        st.caption(link["備註"])
                    st.caption(link.get("網址", ""))
                with action_col:
                    st.link_button("開啟", link.get("網址", ""))

                move_col1, move_col2, delete_col = st.columns(3)
                with move_col1:
                    if st.button("上移", key=f"link_up_{index}", disabled=index == 0):
                        move_link(index, -1)
                        st.rerun()
                with move_col2:
                    if st.button(
                        "下移",
                        key=f"link_down_{index}",
                        disabled=index == len(links) - 1,
                    ):
                        move_link(index, 1)
                        st.rerun()
                with delete_col:
                    if st.button("刪除", key=f"link_delete_{index}"):
                        delete_link(index)
                        st.rerun()
