import streamlit as st

from utils.auth import require_login, logout_button
from utils.github_json_store import storage_label
from utils.template_store import (
    TEMPLATE_CONFIGS,
    delete_template,
    get_template_bytes,
    get_template_record,
    save_uploaded_template,
    template_status_text,
)


st.set_page_config(
    page_title="模板管理 | 茶道社幹部平台",
    page_icon="🍵",
    layout="wide",
)

require_login()

with st.sidebar:
    st.success("已登入")
    logout_button()

st.title("模板管理")
st.caption("更換成果書與活動申請書的預設 Word 模板。")
st.caption(f"儲存位置：{storage_label()}")

st.info("只會替換模板中以 {{...}} 標註的欄位；沒有標註的文字、格式、字型、對齊與表格內容會保留模板原樣。")

for key, config in TEMPLATE_CONFIGS.items():
    label = str(config["label"])
    with st.container(border=True):
        st.subheader(label)
        st.caption(template_status_text(key))

        data, file_name, is_custom = get_template_bytes(key)
        download_name = file_name if file_name.endswith(".docx") else f"{label}.docx"

        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader(
                f"上傳新的{label}",
                type=["docx"],
                key=f"template_upload_{key}",
            )
            if st.button(f"儲存{label}", key=f"template_save_{key}", type="primary"):
                if uploaded_file is None:
                    st.error("請先選擇 .docx 檔案。")
                else:
                    try:
                        save_uploaded_template(key, uploaded_file)
                    except Exception as exc:
                        st.error("模板儲存失敗，請確認檔案是有效的 Word .docx。")
                        st.exception(exc)
                    else:
                        st.success("模板已更新。")
                        st.rerun()

        with col2:
            st.download_button(
                "下載目前模板",
                data=data,
                file_name=download_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"template_download_{key}",
            )
            if st.button(
                "恢復內建模板",
                key=f"template_reset_{key}",
                disabled=not is_custom,
            ):
                delete_template(key)
                st.success("已恢復內建模板。")
                st.rerun()

        with st.expander("可使用的標註欄位", expanded=False):
            for placeholder in config["placeholders"]:
                st.code(str(placeholder), language="text")

        record = get_template_record(key)
        if record:
            st.caption(f"檔案大小：{int(record.get('size', 0)):,} bytes")
