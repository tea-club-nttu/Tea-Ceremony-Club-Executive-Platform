import math
import random

import streamlit as st

from utils.auth import require_login, logout_button


st.set_page_config(
    page_title="時間與角度教學 | 校園活動管理平台",
    page_icon="⏰",
    layout="wide",
)

require_login()


st.markdown(
    """
    <style>
        .learning-hero {
            padding: 18px 20px;
            border: 1px solid #d7e2ea;
            border-radius: 8px;
            background: linear-gradient(135deg, #f7fbfc 0%, #fff8f2 100%);
        }
        .learning-card {
            padding: 16px;
            border: 1px solid #d9e3ea;
            border-radius: 8px;
            background: #ffffff;
            min-height: 100%;
        }
        .math-chip {
            display: inline-block;
            margin: 4px 6px 4px 0;
            padding: 5px 9px;
            border: 1px solid #c9d8df;
            border-radius: 8px;
            background: #f8fbfc;
            font-weight: 650;
        }
        .feedback-good {
            padding: 10px 12px;
            border-left: 5px solid #20875a;
            background: #effaf4;
            border-radius: 6px;
        }
        .feedback-warm {
            padding: 10px 12px;
            border-left: 5px solid #c76528;
            background: #fff6ec;
            border-radius: 6px;
        }
        .svg-wrap {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        .formula-line {
            font-size: 1.05rem;
            line-height: 1.75;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def time_label(hour: int, minute: int) -> str:
    normalized_hour = hour % 24
    return f"{normalized_hour:02d}:{minute:02d}"


def twelve_hour_label(hour: int, minute: int) -> str:
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d}"


def add_minutes(hour: int, minute: int, delta: int) -> tuple[int, int]:
    total = (hour * 60 + minute + delta) % (24 * 60)
    return total // 60, total % 60


def plural_unit(value: int, unit: str) -> str:
    if value <= 0:
        return ""
    return f"{value} {unit}"


def clock_svg(hour: int, minute: int, size: int = 300) -> str:
    center = size / 2
    radius = size * 0.42
    hour_angle = ((hour % 12) + minute / 60) * 30
    minute_angle = minute * 6

    def point(angle: float, length: float) -> tuple[float, float]:
        rad = math.radians(angle - 90)
        return center + math.cos(rad) * length, center + math.sin(rad) * length

    ticks = []
    for value in range(60):
        angle = value * 6
        outer_x, outer_y = point(angle, radius)
        inner = radius - (16 if value % 5 == 0 else 7)
        inner_x, inner_y = point(angle, inner)
        stroke = "#263238" if value % 5 == 0 else "#93a8b0"
        width = 3 if value % 5 == 0 else 1
        ticks.append(
            f'<line x1="{inner_x:.1f}" y1="{inner_y:.1f}" x2="{outer_x:.1f}" y2="{outer_y:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" />'
        )

    numbers = []
    for number in range(1, 13):
        x, y = point(number * 30, radius - 35)
        numbers.append(
            f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" '
            f'font-size="18" font-family="Arial" fill="#263238" font-weight="700">{number}</text>'
        )

    hour_x, hour_y = point(hour_angle, radius * 0.48)
    minute_x, minute_y = point(minute_angle, radius * 0.72)

    return f"""
    <svg viewBox="0 0 {size} {size}" width="100%" height="100%" role="img" aria-label="時鐘">
        <circle cx="{center}" cy="{center}" r="{radius + 14}" fill="#fffdf8" stroke="#2f5f72" stroke-width="7" />
        <circle cx="{center}" cy="{center}" r="{radius + 4}" fill="#ffffff" stroke="#d5e3e8" stroke-width="2" />
        {''.join(ticks)}
        {''.join(numbers)}
        <line x1="{center}" y1="{center}" x2="{hour_x:.1f}" y2="{hour_y:.1f}" stroke="#24495a" stroke-width="9" stroke-linecap="round" />
        <line x1="{center}" y1="{center}" x2="{minute_x:.1f}" y2="{minute_y:.1f}" stroke="#d85c3a" stroke-width="5" stroke-linecap="round" />
        <circle cx="{center}" cy="{center}" r="9" fill="#24495a" />
        <text x="{center}" y="{size - 18}" text-anchor="middle" font-size="17" font-family="Arial" fill="#47606b" font-weight="700">
            {twelve_hour_label(hour, minute)}
        </text>
    </svg>
    """


def angle_type(degrees: int) -> str:
    if degrees == 0:
        return "零角"
    if degrees < 90:
        return "銳角"
    if degrees == 90:
        return "直角"
    if degrees < 180:
        return "鈍角"
    if degrees == 180:
        return "平角"
    if degrees < 360:
        return "優角"
    return "周角"


def protractor_svg(degrees: int, size: int = 360) -> str:
    width = size
    height = int(size * 0.64)
    cx = width / 2
    cy = height * 0.82
    radius = width * 0.39
    angle = max(0, min(180, degrees))
    rad = math.radians(angle)
    arm_x = cx + math.cos(rad) * radius
    arm_y = cy - math.sin(rad) * radius
    arc_end_x = cx + math.cos(rad) * (radius * 0.38)
    arc_end_y = cy - math.sin(rad) * (radius * 0.38)
    large_arc = 1 if angle > 180 else 0

    ticks = []
    labels = []
    for value in range(0, 181, 5):
        tick_rad = math.radians(value)
        outer_x = cx + math.cos(tick_rad) * radius
        outer_y = cy - math.sin(tick_rad) * radius
        inner_length = radius - (17 if value % 10 == 0 else 9)
        inner_x = cx + math.cos(tick_rad) * inner_length
        inner_y = cy - math.sin(tick_rad) * inner_length
        stroke = "#294a56" if value % 10 == 0 else "#8aa0a8"
        width_tick = 2 if value % 10 == 0 else 1
        ticks.append(
            f'<line x1="{inner_x:.1f}" y1="{inner_y:.1f}" x2="{outer_x:.1f}" y2="{outer_y:.1f}" '
            f'stroke="{stroke}" stroke-width="{width_tick}" stroke-linecap="round" />'
        )
        if value % 30 == 0:
            label_x = cx + math.cos(tick_rad) * (radius - 36)
            label_y = cy - math.sin(tick_rad) * (radius - 36)
            labels.append(
                f'<text x="{label_x:.1f}" y="{label_y + 5:.1f}" text-anchor="middle" '
                f'font-size="13" font-family="Arial" fill="#294a56" font-weight="700">{value}</text>'
            )

    return f"""
    <svg viewBox="0 0 {width} {height}" width="100%" height="100%" role="img" aria-label="量角器">
        <path d="M {cx - radius:.1f} {cy:.1f} A {radius:.1f} {radius:.1f} 0 0 1 {cx + radius:.1f} {cy:.1f}"
              fill="#f7fbfc" stroke="#2f5f72" stroke-width="5" />
        <path d="M {cx - radius + 18:.1f} {cy:.1f} A {radius - 18:.1f} {radius - 18:.1f} 0 0 1 {cx + radius - 18:.1f} {cy:.1f}"
              fill="none" stroke="#d7e4ea" stroke-width="2" />
        {''.join(ticks)}
        {''.join(labels)}
        <line x1="{cx - radius - 10:.1f}" y1="{cy:.1f}" x2="{cx + radius + 10:.1f}" y2="{cy:.1f}"
              stroke="#273f49" stroke-width="4" stroke-linecap="round" />
        <path d="M {cx:.1f} {cy:.1f} L {cx + radius * 0.38:.1f} {cy:.1f}
                 A {radius * 0.38:.1f} {radius * 0.38:.1f} 0 {large_arc} 0 {arc_end_x:.1f} {arc_end_y:.1f} Z"
              fill="#f2a65a" opacity="0.35" />
        <line x1="{cx:.1f}" y1="{cy:.1f}" x2="{arm_x:.1f}" y2="{arm_y:.1f}"
              stroke="#d85c3a" stroke-width="6" stroke-linecap="round" />
        <circle cx="{cx:.1f}" cy="{cy:.1f}" r="8" fill="#24495a" />
        <text x="{cx:.1f}" y="{cy - 32:.1f}" text-anchor="middle" font-size="22"
              font-family="Arial" fill="#24495a" font-weight="800">{angle}°</text>
    </svg>
    """


def render_svg(svg: str, height: int) -> None:
    st.markdown(
        f'<div class="svg-wrap" style="height:{height}px">{svg}</div>',
        unsafe_allow_html=True,
    )


def init_quiz() -> None:
    if "math_quiz" in st.session_state:
        return
    st.session_state["math_quiz"] = make_quiz()
    st.session_state["math_quiz_checked"] = False


def make_quiz() -> dict[str, int]:
    start_hour = random.randint(7, 15)
    start_minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    elapsed = random.choice([15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 90, 105, 120])
    end_hour, end_minute = add_minutes(start_hour, start_minute, elapsed)
    quiz_angle = random.choice([25, 45, 60, 90, 110, 135, 150, 180])
    return {
        "start_hour": start_hour,
        "start_minute": start_minute,
        "elapsed": elapsed,
        "end_hour": end_hour,
        "end_minute": end_minute,
        "clock_hour": random.randint(1, 12),
        "clock_minute": random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]),
        "angle": quiz_angle,
    }


with st.sidebar:
    st.success("已登入")
    logout_button()

st.title("國小時間與角度教學")
st.caption("用時鐘、經過時間、量角器和小測驗練習三到六年級常見概念。")

st.markdown(
    """
    <div class="learning-hero">
        <div class="formula-line">
            <span class="math-chip">1 小時 = 60 分鐘</span>
            <span class="math-chip">1 分鐘 = 60 秒</span>
            <span class="math-chip">直角 = 90°</span>
            <span class="math-chip">平角 = 180°</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

time_tab, angle_tab, quiz_tab = st.tabs(["時間教室", "角度教室", "小測驗"])

with time_tab:
    st.subheader("讀時鐘")
    clock_col, concept_col = st.columns([1.05, 1])
    with clock_col:
        with st.container(border=True):
            selected_hour = st.slider("小時", min_value=1, max_value=12, value=3, step=1)
            selected_minute = st.slider("分鐘", min_value=0, max_value=55, value=20, step=5)
            render_svg(clock_svg(selected_hour, selected_minute), 330)

    with concept_col:
        with st.container(border=True):
            st.markdown("#### 指針代表的意思")
            st.write("短針走一大格是 1 小時；長針走一小格是 1 分鐘。")
            st.write("長針走 5 小格，就是 5 分鐘；走一圈，就是 60 分鐘。")
            st.markdown(
                f"""
                <div class="formula-line">
                    這個鐘面是 <strong>{twelve_hour_label(selected_hour, selected_minute)}</strong><br>
                    長針指到第 <strong>{selected_minute // 5}</strong> 個大格，代表 <strong>{selected_minute}</strong> 分鐘。
                </div>
                """,
                unsafe_allow_html=True,
            )
            if selected_minute == 0:
                st.success("整點時，長針會指向 12。")
            elif selected_minute == 30:
                st.success("30 分鐘也可以說成半小時。")
            elif selected_minute == 15:
                st.success("15 分鐘也可以說成一刻鐘。")

    st.subheader("經過時間")
    elapsed_col, result_col = st.columns([1.15, 1])
    with elapsed_col:
        with st.container(border=True):
            start_hour = st.number_input("開始：時", min_value=0, max_value=23, value=8, step=1)
            start_minute = st.selectbox("開始：分", list(range(0, 60, 5)), index=6)
            elapsed_minutes = st.slider("經過幾分鐘", min_value=5, max_value=180, value=45, step=5)
            end_hour, end_minute = add_minutes(start_hour, start_minute, elapsed_minutes)

    with result_col:
        with st.container(border=True):
            hours_part = elapsed_minutes // 60
            minutes_part = elapsed_minutes % 60
            elapsed_text = " ".join(
                item
                for item in [
                    plural_unit(hours_part, "小時"),
                    plural_unit(minutes_part, "分鐘"),
                ]
                if item
            )
            st.metric("結束時間", time_label(end_hour, end_minute))
            st.write(f"從 {time_label(start_hour, start_minute)} 開始，經過 {elapsed_text}。")
            st.markdown(
                f"""
                <div class="formula-line">
                    {start_hour:02d}:{start_minute:02d}
                    ＋ {elapsed_minutes} 分鐘
                    ＝ <strong>{end_hour:02d}:{end_minute:02d}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

with angle_tab:
    st.subheader("認識角度")
    angle_col, rule_col = st.columns([1.1, 1])
    with angle_col:
        with st.container(border=True):
            selected_angle = st.slider("角度", min_value=0, max_value=180, value=65, step=5)
            render_svg(protractor_svg(selected_angle), 300)

    with rule_col:
        with st.container(border=True):
            current_type = angle_type(selected_angle)
            st.metric("角的名稱", current_type)
            st.write("角度越大，兩條邊張開得越寬。")
            st.markdown(
                """
                <div class="formula-line">
                    <span class="math-chip">小於 90°：銳角</span>
                    <span class="math-chip">等於 90°：直角</span>
                    <span class="math-chip">90° 到 180°：鈍角</span>
                    <span class="math-chip">等於 180°：平角</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if current_type == "銳角":
                st.success("這個角比直角小。")
            elif current_type == "直角":
                st.success("這個角剛好像方格紙的角。")
            elif current_type == "鈍角":
                st.success("這個角比直角大，但是還不到平角。")
            elif current_type == "平角":
                st.success("兩條邊排成一直線，就是平角。")

    st.subheader("角度加減")
    split_col, total_col = st.columns([1, 1])
    with split_col:
        with st.container(border=True):
            first_angle = st.slider("第一個角", min_value=0, max_value=180, value=40, step=5)
            second_angle = st.slider("第二個角", min_value=0, max_value=180, value=50, step=5)
            angle_sum = first_angle + second_angle

    with total_col:
        with st.container(border=True):
            st.metric("合起來", f"{angle_sum}°")
            if angle_sum < 90:
                st.info("合起來還是銳角。")
            elif angle_sum == 90:
                st.success("合起來剛好是直角。")
            elif angle_sum < 180:
                st.info("合起來是鈍角。")
            elif angle_sum == 180:
                st.success("合起來剛好是平角。")
            else:
                st.warning("超過平角，國小題目常會拆成 180° 再多一些來想。")
            st.markdown(
                f"""
                <div class="formula-line">
                    {first_angle}° ＋ {second_angle}° ＝ <strong>{angle_sum}°</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

with quiz_tab:
    init_quiz()
    quiz = st.session_state["math_quiz"]

    action_col, score_col = st.columns([1, 3])
    with action_col:
        if st.button("換一組題目", type="secondary"):
            st.session_state["math_quiz"] = make_quiz()
            st.session_state["math_quiz_checked"] = False
            st.rerun()
    with score_col:
        st.caption("完成三題後按下檢查答案。")

    q1_col, q2_col, q3_col = st.columns(3)
    with q1_col:
        with st.container(border=True):
            st.markdown("#### 1. 讀出鐘面時間")
            render_svg(clock_svg(quiz["clock_hour"], quiz["clock_minute"], size=260), 240)
            answer_hour = st.selectbox("答案：時", list(range(1, 13)), key="quiz_hour")
            answer_minute = st.selectbox("答案：分", list(range(0, 60, 5)), key="quiz_minute")

    with q2_col:
        with st.container(border=True):
            st.markdown("#### 2. 算出結束時間")
            st.write(
                f"{time_label(quiz['start_hour'], quiz['start_minute'])} 開始，"
                f"經過 {quiz['elapsed']} 分鐘。"
            )
            elapsed_answer_hour = st.number_input("答案：時", min_value=0, max_value=23, value=quiz["start_hour"], key="elapsed_hour")
            elapsed_answer_minute = st.selectbox("答案：分", list(range(0, 60, 5)), key="elapsed_minute")

    with q3_col:
        with st.container(border=True):
            st.markdown("#### 3. 判斷角的種類")
            render_svg(protractor_svg(quiz["angle"], size=300), 220)
            angle_answer = st.radio("答案", ["銳角", "直角", "鈍角", "平角"], horizontal=True, key="angle_answer")

    if st.button("檢查答案", type="primary"):
        st.session_state["math_quiz_checked"] = True

    if st.session_state.get("math_quiz_checked"):
        correct_clock = answer_hour == (quiz["clock_hour"] % 12 or 12) and answer_minute == quiz["clock_minute"]
        correct_elapsed = elapsed_answer_hour == quiz["end_hour"] and elapsed_answer_minute == quiz["end_minute"]
        correct_angle = angle_answer == angle_type(quiz["angle"])
        score = sum([correct_clock, correct_elapsed, correct_angle])

        st.subheader(f"得分：{score} / 3")
        if correct_clock:
            st.markdown('<div class="feedback-good">第 1 題正確。</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="feedback-warm">第 1 題答案是 {twelve_hour_label(quiz["clock_hour"], quiz["clock_minute"])}。</div>',
                unsafe_allow_html=True,
            )

        if correct_elapsed:
            st.markdown('<div class="feedback-good">第 2 題正確。</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="feedback-warm">第 2 題答案是 {time_label(quiz["end_hour"], quiz["end_minute"])}。</div>',
                unsafe_allow_html=True,
            )

        if correct_angle:
            st.markdown('<div class="feedback-good">第 3 題正確。</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="feedback-warm">第 3 題答案是 {angle_type(quiz["angle"])}。</div>',
                unsafe_allow_html=True,
            )
