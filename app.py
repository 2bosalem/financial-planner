# -*- coding: utf-8 -*-
"""
لوحة التخطيط المالي الذكية — Smart Financial Planning Dashboard (v2)
24-month plan with THREE scenarios:
  1. Standard baseline (static, from day 1)
  2. Actual balances   (user-entered, editable grid)
  3. Extrapolated path (dynamic: re-anchored on the latest actual balance)
Arabic RTL, mobile-first, no traditional charts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------
# Page configuration (centered layout works best on phones)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="لوحة التخطيط المالي الذكية",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

MONTH_NAMES = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]

# ---------------------------------------------------------------
# Global CSS: Arabic font, RTL direction, cards, mobile tweaks
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    html, body, [class*="st-"], .stApp {
        font-family: 'Cairo', sans-serif !important;
    }
    .stApp { direction: rtl; }
    [data-testid="stSidebar"] { direction: rtl; }
    [data-testid="stNumberInput"] input { direction: ltr; text-align: left; }

    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.6rem;
        margin: 0 0 0.4rem 0;
    }
    .app-subtitle {
        text-align: center;
        opacity: 0.7;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    /* AI coach banner */
    .coach-box {
        border-radius: 18px;
        padding: 18px 20px;
        color: #ffffff;
        font-size: 1.02rem;
        font-weight: 700;
        line-height: 1.9;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }
    .coach-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .coach-amber { background: linear-gradient(135deg, #f7971e, #ffd200); color: #3a2c00; }
    .coach-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .coach-info  { background: linear-gradient(135deg, #2b5876, #4e4376); }
    .coach-title { font-size: 0.85rem; opacity: 0.85; font-weight: 400; }
    .coach-traj  {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed rgba(255,255,255,0.45);
        font-size: 0.95rem;
        font-weight: 400;
    }

    /* Metric blocks */
    .metric-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem; }
    .metric-block {
        flex: 1 1 40%;
        min-width: 140px;
        border-radius: 14px;
        padding: 12px 8px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .metric-label { font-size: 0.78rem; opacity: 0.9; }
    .metric-value { font-size: 1.15rem; font-weight: 900; direction: ltr; }
    .mb-blue  { background: linear-gradient(135deg, #396afc, #2948ff); }
    .mb-gray  { background: linear-gradient(135deg, #556270, #4ecdc4); }
    .mb-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .mb-amber { background: linear-gradient(135deg, #f7971e, #ffb200); }
    .mb-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }

    /* Milestone cards */
    .milestone-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem; }
    .milestone {
        flex: 1 1 45%;
        min-width: 150px;
        border-radius: 14px;
        padding: 12px 14px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .milestone h4 { margin: 0 0 4px 0; font-size: 0.95rem; }
    .milestone .amt { font-size: 1.1rem; font-weight: 900; direction: ltr; display: inline-block; }
    .milestone .when { font-size: 0.8rem; opacity: 0.9; }
    .ms-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .ms-amber { background: linear-gradient(135deg, #f7971e, #ffb200); color: #3a2c00; }
    .ms-green { background: linear-gradient(135deg, #11998e, #38ef7d); }

    .section-title {
        font-weight: 900;
        font-size: 1.1rem;
        margin: 0.6rem 0 0.4rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt(x: float) -> str:
    """Format a number with thousands separators, no decimals."""
    return f"{x:,.0f}"


def project_month(prev_balance: float, obligation: float, salary: float, spend_limit: float) -> float:
    """Core formula: ((prev - obligations) + salary) - target spending limit."""
    return (prev_balance - obligation) + salary - spend_limit


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown('<div class="app-title">💰 لوحة التخطيط المالي الذكية</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">خطة ٢٤ شهرًا • المعياري الثابت × الفعلي × التوقع المحدث</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# 1) Base inputs
# ---------------------------------------------------------------
with st.expander("⚙️ الإعدادات الأساسية", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        start_month = st.selectbox(
            "شهر بداية الخطة",
            options=list(range(1, 13)),
            format_func=lambda m: MONTH_NAMES[m - 1],
            index=0,
        )
        initial_balance = st.number_input("الرصيد الافتتاحي (النقد)", value=10000.0, step=500.0)
        currency = st.text_input("رمز العملة", value="ر.س", max_chars=8)
    with c2:
        start_year = st.number_input("سنة بداية الخطة", min_value=2020, max_value=2100, value=2026, step=1)
        salary = st.number_input("الراتب الشهري", min_value=0.0, value=8000.0, step=250.0)
        spend_limit = st.number_input("حد الصرف الشهري المستهدف", min_value=0.0, value=6000.0, step=250.0)

# ---------------------------------------------------------------
# 2) Annual obligations (4 items)
# ---------------------------------------------------------------
with st.expander("📌 الالتزامات السنوية (٤ بنود)", expanded=False):
    st.caption("حدد اسم كل التزام ومبلغه ورقم الشهر الذي يُستحق فيه (من 1 إلى 24).")
    default_obligations = [
        ("تأمين السيارة", 3000.0, 3),
        ("رسوم المدارس", 6000.0, 8),
        ("صيانة / إيجار سنوي", 4000.0, 12),
        ("سفر العائلة", 5000.0, 18),
    ]
    obligations = []
    for i, (d_name, d_amount, d_month) in enumerate(default_obligations, start=1):
        c1, c2, c3 = st.columns([2.0, 1.3, 1.0])
        name = c1.text_input(f"اسم الالتزام {i}", value=d_name, key=f"ob_name_{i}")
        amount = c2.number_input("المبلغ", min_value=0.0, value=d_amount, step=500.0, key=f"ob_amount_{i}")
        month = c3.number_input("الشهر", min_value=1, max_value=24, value=d_month, step=1, key=f"ob_month_{i}")
        obligations.append((name.strip() or f"التزام {i}", float(amount), int(month)))

# ---------------------------------------------------------------
# Timeline labels
# ---------------------------------------------------------------
month_labels = []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")

obligations_per_month = [
    sum(amount for _, amount, due in obligations if due == i + 1) for i in range(24)
]

# ---------------------------------------------------------------
# Session persistence for the 24 "Actual Balance" inputs
# ---------------------------------------------------------------
if "actual_balances" not in st.session_state:
    st.session_state.actual_balances = [None] * 24
actuals = st.session_state.actual_balances

# ---------------------------------------------------------------
# Scenario 1 — Standard baseline (STATIC, anchored on day-1 inputs only)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(24):
    prev = project_month(prev, obligations_per_month[i], float(salary), float(spend_limit))
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Scenario 3 — Extrapolated path (DYNAMIC, re-anchored on actual data)
#   * month with an actual entry  -> extrapolated = actual (reality wins)
#   * month without an entry      -> projected from the previous
#     extrapolated value, so every future month automatically chains
#     from the LATEST actual balance the user entered.
# ---------------------------------------------------------------
extrapolated_balances = []
prev_ext = float(initial_balance)
for i in range(24):
    if actuals[i] is not None:
        value = float(actuals[i])
    else:
        value = project_month(prev_ext, obligations_per_month[i], float(salary), float(spend_limit))
    extrapolated_balances.append(value)
    prev_ext = value

filled_idx = [i for i, v in enumerate(actuals) if v is not None]

# Placeholders so the coach / gauges / cards render at the TOP of the page,
# while the editable grid lives further below.
coach_area = st.container()
gauge_area = st.container()
metrics_area = st.container()
milestones_area = st.container()

# ---------------------------------------------------------------
# Editable data grid — all 3 scenario columns
# ---------------------------------------------------------------
st.markdown('<div class="section-title">📋 سجل الأرصدة الشهرية (24 شهرًا)</div>', unsafe_allow_html=True)
st.caption(
    "أدخل رصيدك الحقيقي في عمود «الرصيد الفعلي». عمود «التوقع المحدث» يعيد رسم مستقبلك "
    "تلقائيًا انطلاقًا من آخر رصيد فعلي أدخلته، بينما يبقى «المعياري الثابت» خطتك الأصلية للمقارنة."
)

grid_df = pd.DataFrame(
    {
        "الشهر": month_labels,
        "التزامات الشهر": obligations_per_month,
        "المعياري الثابت": standard_balances,
        "الرصيد الفعلي": pd.array(actuals, dtype="Float64"),
        "التوقع المحدث": extrapolated_balances,
    }
)

edited_df = st.data_editor(
    grid_df,
    hide_index=True,
    use_container_width=True,
    height=430,
    disabled=["الشهر", "التزامات الشهر", "المعياري الثابت", "التوقع المحدث"],
    column_config={
        "الشهر": st.column_config.TextColumn("الشهر", width="medium"),
        "التزامات الشهر": st.column_config.NumberColumn("التزامات", format="%.0f"),
        "المعياري الثابت": st.column_config.NumberColumn(
            "المعياري الثابت 📐", format="%.0f", help="الخطة النظرية الأصلية منذ اليوم الأول — لا تتغير"
        ),
        "الرصيد الفعلي": st.column_config.NumberColumn(
            "الرصيد الفعلي ✍️", format="%.0f", help="رصيدك الحقيقي في بداية الشهر — هذا العمود قابل للتعديل"
        ),
        "التوقع المحدث": st.column_config.NumberColumn(
            "التوقع المحدث 🔮", format="%.0f", help="مسار مستقبلي مُعاد حسابه من آخر رصيد فعلي أدخلته"
        ),
    },
)

# Persist edits, then rerun once so the extrapolated column, gauges and
# coach all reflect the new entry immediately (no stale values).
new_actuals = [None if pd.isna(v) else float(v) for v in edited_df["الرصيد الفعلي"]]
if new_actuals != st.session_state.actual_balances:
    st.session_state.actual_balances = new_actuals
    st.rerun()

st.progress(len(filled_idx) / 24, text=f"أدخلت {len(filled_idx)} من 24 شهرًا")

# ---------------------------------------------------------------
# Health status — current position (latest actual vs original baseline)
# ---------------------------------------------------------------
def zone_of(diff: float, ref: float) -> str:
    pct = diff / ref * 100.0
    if diff >= 0:
        return "green"
    if pct >= -10.0:
        return "amber"
    return "red"


if filled_idx:
    idx = max(filled_idx)
    actual_now = actuals[idx]
    standard_now = standard_balances[idx]
    diff_now = actual_now - standard_now
    ref_now = max(abs(standard_now), 1.0)
    pct_now = diff_now / ref_now * 100.0
    status_now = zone_of(diff_now, ref_now)

    # --- Future trajectory: the extrapolated path beyond the latest entry ---
    future_ids = list(range(idx + 1, 24))
    if future_ids:
        fut_vals = [extrapolated_balances[i] for i in future_ids]
        fut_min = min(fut_vals)
        fut_min_i = future_ids[fut_vals.index(fut_min)]
        end_ext = extrapolated_balances[23]
        end_std = standard_balances[23]
        end_diff = end_ext - end_std
        end_ref = max(abs(end_std), 1.0)
        end_pct = end_diff / end_ref * 100.0
        if fut_min < 0:
            status_traj = "red"
        else:
            status_traj = zone_of(end_diff, end_ref)
    else:
        fut_min = fut_min_i = None
        end_ext, end_std = extrapolated_balances[23], standard_balances[23]
        end_diff = end_ext - end_std
        end_pct = end_diff / max(abs(end_std), 1.0) * 100.0
        status_traj = status_now
else:
    idx = None
    status_now = status_traj = "info"

SEVERITY = {"green": 0, "amber": 1, "red": 2}

# ---------------------------------------------------------------
# AI Financial Coach (top banner) — current position + future trajectory
# ---------------------------------------------------------------
with coach_area:
    if status_now == "info":
        banner_class = "coach-info"
        body = (
            "👋 أهلًا بك! أدخل رصيدك الفعلي لأول شهر في الجدول بالأسفل، وسأبدأ فورًا "
            "بتحليل وضعك الحالي وإعادة رسم توقعات مستقبلك المالي شهرًا بشهر."
        )
        traj_line = ""
    else:
        # Line 1 — where you stand TODAY vs the original plan
        if status_now == "green":
            body = (
                f"🎉 عمل رائع! في <b>{month_labels[idx]}</b> أنت متقدم على الخطة الأصلية بنسبة "
                f"<b>{abs(pct_now):.1f}%</b> (+{fmt(diff_now)} {currency})."
            )
        elif status_now == "amber":
            body = (
                f"⚠️ انتبه! في <b>{month_labels[idx]}</b> رصيدك أدنى من الخطة الأصلية بمقدار "
                f"<b>{fmt(abs(diff_now))} {currency}</b> ({abs(pct_now):.1f}%). أنت في منطقة الحذر."
            )
        else:
            daily_cut = abs(diff_now) / 30.0
            body = (
                f"🚨 تحذير: في <b>{month_labels[idx]}</b> أنت داخل المنطقة غير المريحة بمقدار "
                f"<b>{fmt(abs(diff_now))} {currency}</b> ({abs(pct_now):.1f}% تحت الهدف). "
                f"قلّل صرفك اليومي بحوالي <b>{fmt(daily_cut)} {currency}</b>."
            )

        # Line 2 — where your UPDATED trajectory is heading
        if status_traj == "red" and fut_min is not None and fut_min < 0:
            traj_line = (
                f"🔮 <b>المسار المستقبلي:</b> إذا استمررت على هذا الوضع، يتوقع النموذج أن يهبط رصيدك إلى "
                f"<b>{fmt(fut_min)} {currency}</b> في <b>{month_labels[fut_min_i]}</b> — "
                f"أي دخول المنطقة غير المريحة. خفّض الصرف الآن قبل الوصول لتلك المحطة."
            )
        elif status_traj == "red":
            traj_line = (
                f"🔮 <b>المسار المستقبلي:</b> توقعك المحدث لنهاية الخطة (<b>{fmt(end_ext)} {currency}</b>) "
                f"أدنى بكثير من الهدف الأصلي (<b>{fmt(end_std)} {currency}</b>) بفارق {fmt(abs(end_diff))} {currency}."
            )
        elif status_traj == "amber":
            traj_line = (
                f"🔮 <b>المسار المستقبلي:</b> مسارك المحدث ينحرف قليلًا عن الخطة — متوقع أن تنهي الخطة عند "
                f"<b>{fmt(end_ext)} {currency}</b> مقابل هدف <b>{fmt(end_std)} {currency}</b> "
                f"({abs(end_pct):.1f}% أدنى). انحراف قابل للتصحيح بسهولة."
            )
        else:
            traj_line = (
                f"🔮 <b>المسار المستقبلي:</b> ممتاز — توقعك المحدث لنهاية الخطة "
                f"<b>{fmt(end_ext)} {currency}</b> يساوي أو يتجاوز الهدف الأصلي ({fmt(end_std)} {currency})."
            )

        # Banner colour reflects the WORSE of (today, trajectory)
        worst = status_now if SEVERITY[status_now] >= SEVERITY[status_traj] else status_traj
        banner_class = {"green": "coach-green", "amber": "coach-amber", "red": "coach-red"}[worst]

    traj_html = f'<div class="coach-traj">{traj_line}</div>' if traj_line else ""
    st.markdown(
        f'<div class="coach-box {banner_class}">'
        f'<div class="coach-title">🤖 مدربك المالي الذكي</div>{body}{traj_html}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Health gauges: (1) current month vs baseline  (2) end-of-plan trajectory
# ---------------------------------------------------------------
def make_gauge(title: str, value: float, target: float, currency: str) -> go.Figure:
    ref = max(abs(target), 1.0)
    lo = min(0.0, value, target)
    hi = max(value, target, 1.0)
    span = max(hi - lo, 1.0)
    rng_min = lo - 0.05 * span
    rng_max = hi + 0.15 * span
    amber_low = target - 0.10 * ref  # bottom of the caution zone

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            number={"valueformat": ",.0f", "suffix": f" {currency}", "font": {"size": 26}},
            delta={"reference": target, "valueformat": ",.0f"},
            title={"text": title, "font": {"size": 14}},
            gauge={
                "axis": {"range": [rng_min, rng_max], "tickformat": ",.0f"},
                "bar": {"color": "#1f2a44", "thickness": 0.28},
                "steps": [
                    {"range": [rng_min, amber_low], "color": "#ef5350"},
                    {"range": [amber_low, target], "color": "#ffca28"},
                    {"range": [target, rng_max], "color": "#66bb6a"},
                ],
                "threshold": {
                    "line": {"color": "#1f2a44", "width": 4},
                    "thickness": 0.9,
                    "value": target,
                },
            },
        )
    )
    fig.update_layout(
        height=240,
        margin=dict(l=25, r=25, t=55, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Cairo, sans-serif"},
    )
    return fig


with gauge_area:
    if idx is not None:
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(
                make_gauge(f"الوضع الحالي — {month_labels[idx]}", actual_now, standard_now, currency),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with g2:
            st.plotly_chart(
                make_gauge("توقع نهاية الخطة (شهر 24)", end_ext, end_std, currency),
                use_container_width=True,
                config={"displayModeBar": False},
            )

with metrics_area:
    if idx is not None:
        now_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_now]
        traj_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_traj]
        diff_sign = "+" if diff_now >= 0 else "−"
        st.markdown(
            f"""
            <div class="metric-row">
              <div class="metric-block mb-blue">
                <div class="metric-label">الرصيد الفعلي الآن</div>
                <div class="metric-value">{fmt(actual_now)}</div>
              </div>
              <div class="metric-block mb-gray">
                <div class="metric-label">المعياري الثابت الآن</div>
                <div class="metric-value">{fmt(standard_now)}</div>
              </div>
              <div class="metric-block {now_class}">
                <div class="metric-label">الفرق الحالي</div>
                <div class="metric-value">{diff_sign}{fmt(abs(diff_now))}</div>
              </div>
              <div class="metric-block {traj_class}">
                <div class="metric-label">التوقع المحدث لنهاية الخطة</div>
                <div class="metric-value">{fmt(end_ext)}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------
# Future milestone cards (upcoming annual obligations)
# ---------------------------------------------------------------
with milestones_area:
    st.markdown('<div class="section-title">🗓️ المحطات القادمة — الالتزامات السنوية</div>', unsafe_allow_html=True)

    current_position = (max(filled_idx) + 2) if filled_idx else 1  # next month number (1-24)
    upcoming = sorted(
        [ob for ob in obligations if ob[1] > 0 and ob[2] >= current_position],
        key=lambda ob: ob[2],
    )

    if not upcoming:
        st.info("✅ لا توجد التزامات سنوية متبقية في الفترة القادمة من خطتك.")
    else:
        cards_html = '<div class="milestone-row">'
        for name, amount, due in upcoming:
            months_away = due - current_position
            if months_away <= 1:
                cls, when = "ms-red", ("⏰ هذا الشهر!" if months_away <= 0 else "⏰ الشهر القادم!")
            elif months_away <= 3:
                cls, when = "ms-amber", f"بعد {months_away} أشهر"
            else:
                cls, when = "ms-green", f"بعد {months_away} شهرًا"
            # Show the expected balance right after paying this obligation
            after_balance = extrapolated_balances[due - 1]
            cards_html += (
                f'<div class="milestone {cls}">'
                f"<h4>📌 {name}</h4>"
                f'<span class="amt">{fmt(amount)} {currency}</span><br>'
                f'<span class="when">{month_labels[due - 1]} • {when}</span><br>'
                f'<span class="when">الرصيد المتوقع بعده: {fmt(after_balance)} {currency}</span>'
                f"</div>"
            )
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.caption(
    "💡 المعياري الثابت = خطتك النظرية من اليوم الأول ولا يتغير. التوقع المحدث = يساوي رصيدك الفعلي "
    "في الأشهر المُدخلة، ثم يعيد إسقاط بقية الأشهر انطلاقًا من آخر رصيد فعلي بنفس القاعدة: "
    "(الرصيد السابق − التزامات الشهر) + الراتب − حد الصرف. تُحفظ مدخلاتك طوال الجلسة."
)
