import altair as alt
import pandas as pd
import streamlit as st

from utils.achievement_report import read_questionnaire, should_exclude_question
from utils.auth import require_login, logout_button


st.set_page_config(
    page_title="問卷分析 | 茶道社幹部平台",
    page_icon="🍵",
    layout="wide",
)

require_login()


def clean_values(series: pd.Series, *, include_blank: bool) -> pd.Series:
    values = series.astype(str).str.strip()
    values = values.replace({"nan": "", "NaN": "", "None": ""})
    if include_blank:
        return values.replace("", "未填答")
    return values[values != ""]


def chart_data(df: pd.DataFrame, column: str, *, include_blank: bool) -> pd.DataFrame:
    values = clean_values(df[column], include_blank=include_blank)
    counts = values.value_counts(dropna=False).reset_index()
    counts.columns = ["選項", "份數"]
    total = counts["份數"].sum()
    if total == 0:
        return pd.DataFrame(columns=["選項", "份數", "百分比", "百分比標籤"])

    counts["百分比"] = counts["份數"] / total * 100
    counts["百分比標籤"] = counts["百分比"].map(lambda value: f"{value:.1f}%")
    return counts


def pie_chart(data: pd.DataFrame, title: str) -> alt.Chart:
    base = alt.Chart(data).encode(
        theta=alt.Theta("份數:Q", stack=True),
        color=alt.Color("選項:N", legend=alt.Legend(title="選項")),
        tooltip=[
            alt.Tooltip("選項:N"),
            alt.Tooltip("份數:Q"),
            alt.Tooltip("百分比:Q", format=".1f", title="百分比"),
        ],
    )
    pie = base.mark_arc(outerRadius=120)
    labels = base.mark_text(radius=142, size=14, fontWeight="bold").encode(
        text=alt.Text("百分比標籤:N"),
        color=alt.value("#222222"),
    )
    return (pie + labels).properties(title=title, height=320)


with st.sidebar:
    st.success("已登入")
    logout_button()

st.title("問卷分析")
st.caption("匯入問卷資料，選擇題目後產生圓餅圖與百分比標籤。")

uploaded_file = st.file_uploader("上傳問卷資料", type=["xlsx", "csv"])

if not uploaded_file:
    st.info("請上傳 Excel 或 CSV 問卷資料。")
    st.stop()

try:
    df = read_questionnaire(uploaded_file).dropna(axis=1, how="all")
except Exception as exc:
    st.error("問卷資料讀取失敗，請確認 Excel / CSV 格式是否正確。")
    st.exception(exc)
    st.stop()

columns = [str(column) for column in df.columns]
default_columns = [column for column in columns if not should_exclude_question(column)]

st.subheader("分析摘要")
metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("回覆數", len(df))
metric_col2.metric("題目欄位", len(columns))
metric_col3.metric("預設分析題目", len(default_columns))

st.subheader("圓餅圖設定")
settings_col1, settings_col2 = st.columns([3, 1])
with settings_col1:
    selected_columns = st.multiselect(
        "選擇要產生圓餅圖的題目",
        columns,
        default=default_columns[:3],
        help="姓名、學校、社課名稱、消息來源等欄位預設不選，但仍可手動加入。",
    )
with settings_col2:
    include_blank = st.checkbox("包含未填答", value=False)

if not selected_columns:
    st.warning("請至少選擇一個題目產生圓餅圖。")
else:
    for column in selected_columns:
        data = chart_data(df, column, include_blank=include_blank)
        st.markdown(f"#### {column}")

        if data.empty:
            st.info("此題沒有可分析的有效回覆。")
            continue

        chart_col, table_col = st.columns([2, 1])
        with chart_col:
            st.altair_chart(pie_chart(data, column), use_container_width=True)
        with table_col:
            display_data = data.copy()
            display_data["百分比"] = display_data["百分比"].map(lambda value: f"{value:.1f}%")
            st.dataframe(display_data, hide_index=True, use_container_width=True)

st.subheader("資料預覽")
st.dataframe(df.head(50), use_container_width=True)
