# -*- coding: utf-8 -*-
"""
لوحة التخطيط المالي الذكية — Smart Financial Planning Dashboard
Streamlit app: 24-month plan, Standard vs Actual scenarios,
AI coach message, health gauge, and milestone cards. Arabic RTL, mobile-first.
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
        font-size: 1.05rem;
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

    /* Metric blocks */
    .metric-row { display: flex; gap: 10px; margin-bottom: 1rem; }
    .metric-block {
        flex: 1;
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


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown('<div class="app-title">💰 لوحة التخطيط المالي الذكية</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">خطة ٢٤ شهرًا • السيناريو المستهدف مقابل الواقع الفعلي</div>', unsafe_allow_html=True)

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
# Timeline labels + Standard (baseline) scenario
# Target Balance = ((Prev Balance - Obligations this month) + Salary) - Spend Limit
# ---------------------------------------------------------------
month_labels = []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")

obligations_per_month = [
    sum(amount for _, amount, due in obligations if due == i + 1) for i in range(24)
]

standard_balances = []
prev = float(initial_balance)
for i in range(24):
    prev = (prev - obligations_per_month[i]) + float(salary) - float(spend_limit)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Session persistence for the 24 "Actual Balance" inputs
# ---------------------------------------------------------------
if "actual_balances" not in st.session_state:
    st.session_state.actual_balances = [None] * 24

# Placeholders so the coach / gauge / cards render at the TOP of the page,
# while their values come from the data editor rendered further below.
coach_area = st.container()
gauge_area = st.container()
metrics_area = st.container()
milestones_area = st.container()

# ---------------------------------------------------------------
# Editable data grid (Actual scenario)
# ---------------------------------------------------------------
st.markdown('<div class="section-title">📋 سجل الأرصدة الشهرية (24 شهرًا)</div>', unsafe_allow_html=True)
st.caption("أدخل رصيدك الفعلي في بداية كل شهر في عمود «الرصيد الفعلي». تُحفظ القيم تلقائيًا خلال الجلسة.")

grid_df = pd.DataFrame(
    {
        "الشهر": month_labels,
        "التزامات الشهر": obligations_per_month,
        "الرصيد المستهدف": standard_balances,
        "الرصيد الفعلي": pd.array(st.session_state.actual_balances, dtype="Float64"),
    }
)

edited_df = st.data_editor(
    grid_df,
    hide_index=True,
    use_container_width=True,
    height=430,
    disabled=["الشهر", "التزامات الشهر", "الرصيد المستهدف"],
    column_config={
        "الشهر": st.column_config.TextColumn("الشهر", width="medium"),
        "التزامات الشهر": st.column_config.NumberColumn("التزامات الشهر", format="%.0f"),
        "الرصيد المستهدف": st.column_config.NumberColumn("الرصيد المستهدف", format="%.0f"),
        "الرصيد الفعلي": st.column_config.NumberColumn(
            "الرصيد الفعلي ✍️", format="%.0f", help="رصيدك الحقيقي في بداية الشهر"
        ),
    },
)

# Persist edits back into session_state
st.session_state.actual_balances = [
    None if pd.isna(v) else float(v) for v in edited_df["الرصيد الفعلي"]
]
actuals = st.session_state.actual_balances

filled_idx = [i for i, v in enumerate(actuals) if v is not None]
st.progress(
    len(filled_idx) / 24,
    text=f"أدخلت {len(filled_idx)} من 24 شهرًا",
)

# ---------------------------------------------------------------
# Health status calculation (based on latest month with actual data)
# ---------------------------------------------------------------
if filled_idx:
    idx = max(filled_idx)
    actual_now = actuals[idx]
    standard_now = standard_balances[idx]
    diff = actual_now - standard_now
    ref = max(abs(standard_now), 1.0)
    pct = diff / ref * 100.0

    if diff >= 0:
        status = "green"
    elif pct >= -10.0:
        status = "amber"
    else:
        status = "red"
else:
    idx = None
    status = "info"

# ---------------------------------------------------------------
# 3) AI Financial Coach (top banner)
# ---------------------------------------------------------------
with coach_area:
    if status == "info":
        msg = "👋 أهلًا بك! أدخل رصيدك الفعلي لأول شهر في الجدول بالأسفل، وسأبدأ فورًا بتحليل صحتك المالية وتقديم نصائح مخصصة لك."
        css_class = "coach-info"
    elif status == "green":
        msg = (
            f"🎉 عمل رائع! في <b>{month_labels[idx]}</b> أنت متقدم على حد الأمان بنسبة "
            f"<b>{abs(pct):.1f}%</b> (+{fmt(diff)} {currency}). "
            f"استمر على هذا النهج وفكّر في توجيه الفائض نحو الادخار أو الاستثمار."
        )
        css_class = "coach-green"
    elif status == "amber":
        msg = (
            f"⚠️ انتبه! في <b>{month_labels[idx]}</b> رصيدك أدنى من الخطة بمقدار "
            f"<b>{fmt(abs(diff))} {currency}</b> ({abs(pct):.1f}%). "
            f"أنت في منطقة الحذر — راقب مصروفك اليومي هذا الشهر لتعود إلى المسار."
        )
        css_class = "coach-amber"
    else:
        daily_cut = abs(diff) / 30.0
        msg = (
            f"🚨 تحذير: في <b>{month_labels[idx]}</b> دخلت المنطقة غير المريحة بمقدار "
            f"<b>{fmt(abs(diff))} {currency}</b> ({abs(pct):.1f}% تحت الهدف). "
            f"قلّل صرفك اليومي بحوالي <b>{fmt(daily_cut)} {currency}</b> حتى نهاية الشهر لتصحيح المسار."
        )
        css_class = "coach-red"

    st.markdown(
        f'<div class="coach-box {css_class}">'
        f'<div class="coach-title">🤖 مدربك المالي الذكي</div>{msg}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# 1) Dynamic health gauge + colored metric blocks
# ---------------------------------------------------------------
with gauge_area:
    if idx is not None:
        lo = min(0.0, actual_now, standard_now)
        hi = max(actual_now, standard_now, 1.0)
        span = max(hi - lo, 1.0)
        rng_min = lo - 0.05 * span
        rng_max = hi + 0.15 * span
        amber_low = standard_now - 0.10 * ref  # bottom of the caution zone

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=actual_now,
                number={"valueformat": ",.0f", "suffix": f" {currency}"},
                delta={"reference": standard_now, "valueformat": ",.0f"},
                title={"text": f"مؤشر الصحة المالية — {month_labels[idx]}", "font": {"size": 15}},
                gauge={
                    "axis": {"range": [rng_min, rng_max], "tickformat": ",.0f"},
                    "bar": {"color": "#1f2a44", "thickness": 0.28},
                    "steps": [
                        {"range": [rng_min, amber_low], "color": "#ef5350"},
                        {"range": [amber_low, standard_now], "color": "#ffca28"},
                        {"range": [standard_now, rng_max], "color": "#66bb6a"},
                    ],
                    "threshold": {
                        "line": {"color": "#1f2a44", "width": 4},
                        "thickness": 0.9,
                        "value": standard_now,
                    },
                },
            )
        )
        fig.update_layout(
            height=270,
            margin=dict(l=30, r=30, t=60, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Cairo, sans-serif"},
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with metrics_area:
    if idx is not None:
        diff_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status]
        diff_sign = "+" if diff >= 0 else "−"
        st.markdown(
            f"""
            <div class="metric-row">
              <div class="metric-block mb-blue">
                <div class="metric-label">الرصيد الفعلي</div>
                <div class="metric-value">{fmt(actual_now)}</div>
              </div>
              <div class="metric-block mb-gray">
                <div class="metric-label">الرصيد المستهدف</div>
                <div class="metric-value">{fmt(standard_now)}</div>
              </div>
              <div class="metric-block {diff_class}">
                <div class="metric-label">الفرق</div>
                <div class="metric-value">{diff_sign}{fmt(abs(diff))}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------
# 3) Future milestone cards (upcoming annual obligations)
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
            cards_html += (
                f'<div class="milestone {cls}">'
                f"<h4>📌 {name}</h4>"
                f'<span class="amt">{fmt(amount)} {currency}</span><br>'
                f'<span class="when">{month_labels[due - 1]} • {when}</span>'
                f"</div>"
            )
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.caption(
    "💡 القاعدة الحسابية: الرصيد المستهدف = (رصيد الشهر السابق − التزامات الشهر) + الراتب − حد الصرف المستهدف. "
    "تُحفظ مدخلاتك طوال الجلسة الحالية."
)
