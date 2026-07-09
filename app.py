# -*- coding: utf-8 -*-
"""
لوحة التخطيط المالي الذكية — Smart Financial Planning Dashboard (v3)
Ultra-clean mobile-first UI:
  * One anchor input ("Current Status Update") instead of an editable grid
  * Dynamic reforecasting from the anchor month forward
  * Single end-of-plan health gauge + coach + milestone cards
  * Two-column projection table
Arabic RTL, no traditional charts.
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
# Global CSS — Arabic typography, RTL, airy cards, mobile stacking
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

    /* Extra breathing room between blocks */
    [data-testid="stVerticalBlock"] { gap: 0.9rem; }

    /* Rounded bordered containers (st.container(border=True)) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }

    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.55rem;
        margin: 0 0 0.2rem 0;
    }
    .app-subtitle {
        text-align: center;
        opacity: 0.65;
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
    }

    /* AI coach banner */
    .coach-box {
        border-radius: 20px;
        padding: 20px 22px;
        color: #ffffff;
        font-size: 1.0rem;
        font-weight: 700;
        line-height: 2.0;
        box-shadow: 0 8px 22px rgba(0,0,0,0.16);
    }
    .coach-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .coach-amber { background: linear-gradient(135deg, #f7971e, #ffd200); color: #3a2c00; }
    .coach-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .coach-info  { background: linear-gradient(135deg, #2b5876, #4e4376); }
    .coach-title { font-size: 0.82rem; opacity: 0.85; font-weight: 400; }
    .coach-traj  {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed rgba(255,255,255,0.45);
        font-size: 0.93rem;
        font-weight: 400;
    }

    /* Metric blocks — flex, stack beautifully on narrow screens */
    .metric-row { display: flex; flex-wrap: wrap; gap: 12px; }
    .metric-block {
        flex: 1 1 42%;
        min-width: 140px;
        border-radius: 16px;
        padding: 14px 10px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 5px 14px rgba(0,0,0,0.13);
    }
    .metric-label { font-size: 0.78rem; opacity: 0.92; }
    .metric-value { font-size: 1.2rem; font-weight: 900; direction: ltr; }
    .mb-blue  { background: linear-gradient(135deg, #396afc, #2948ff); }
    .mb-gray  { background: linear-gradient(135deg, #556270, #4ecdc4); }
    .mb-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .mb-amber { background: linear-gradient(135deg, #f7971e, #ffb200); }
    .mb-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }

    /* Milestone cards */
    .milestone-row { display: flex; flex-wrap: wrap; gap: 12px; }
    .milestone {
        flex: 1 1 45%;
        min-width: 150px;
        border-radius: 16px;
        padding: 14px 16px;
        color: #ffffff;
        box-shadow: 0 5px 14px rgba(0,0,0,0.13);
    }
    .milestone h4 { margin: 0 0 4px 0; font-size: 0.95rem; }
    .milestone .amt { font-size: 1.1rem; font-weight: 900; direction: ltr; display: inline-block; }
    .milestone .when { font-size: 0.8rem; opacity: 0.92; }
    .ms-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .ms-amber { background: linear-gradient(135deg, #f7971e, #ffb200); color: #3a2c00; }
    .ms-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }

    .section-title {
        font-weight: 900;
        font-size: 1.08rem;
        margin: 0.2rem 0 0.1rem 0;
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


def zone_of(diff: float, ref: float) -> str:
    """Green at/above target, amber within 10% below, red beyond."""
    if diff >= 0:
        return "green"
    if diff / ref * 100.0 >= -10.0:
        return "amber"
    return "red"


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown('<div class="app-title">💰 لوحة التخطيط المالي الذكية</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">خطة ٢٤ شهرًا • إعادة توقع ديناميكية من وضعك الحالي</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# Plan settings (collapsed — set once, then forget)
# ---------------------------------------------------------------
with st.expander("⚙️ إعدادات الخطة الأساسية", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        start_month = st.selectbox(
            "شهر بداية الخطة",
            options=list(range(1, 13)),
            format_func=lambda m: MONTH_NAMES[m - 1],
            index=0,
            key="start_month",
        )
        initial_balance = st.number_input("الرصيد الافتتاحي (النقد)", value=10000.0, step=500.0, key="init_balance")
        currency = st.text_input("رمز العملة", value="ر.س", max_chars=8, key="currency")
    with c2:
        start_year = st.number_input("سنة بداية الخطة", min_value=2020, max_value=2100, value=2026, step=1, key="start_year")
        salary = st.number_input("الراتب الشهري", min_value=0.0, value=8000.0, step=250.0, key="salary")
        spend_limit = st.number_input("حد الصرف الشهري المستهدف", min_value=0.0, value=6000.0, step=250.0, key="spend_limit")

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
# Timeline + Standard baseline (static original plan)
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
    prev = project_month(prev, obligations_per_month[i], float(salary), float(spend_limit))
    standard_balances.append(prev)

# ---------------------------------------------------------------
# "Current Status Update" — the single anchor input (replaces the grid)
# Widget keys keep the selection + balance in st.session_state seamlessly.
# ---------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="section-title">🧭 تحديث الوضع الحالي</div>', unsafe_allow_html=True)
    st.caption("اختر الشهر الذي أنت فيه الآن وأدخل رصيدك الحقيقي — وسيُعاد توقع كل الأشهر القادمة تلقائيًا.")
    c1, c2 = st.columns(2)
    with c1:
        anchor_idx = st.selectbox(
            "الشهر الحالي",
            options=list(range(24)),
            format_func=lambda i: f"{i + 1} — {month_labels[i]}",
            index=0,
            key="anchor_month_idx",
        )
    with c2:
        anchor_balance = st.number_input(
            "الرصيد الفعلي الحالي",
            value=None,
            step=500.0,
            placeholder="أدخل رصيدك الحقيقي هنا…",
            key="anchor_balance",
        )

has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Adaptive extrapolation (dynamic reforecasting)
#   * months BEFORE the anchor : original standard baseline
#   * the anchor month         : exactly the user's input
#   * months AFTER the anchor  : chained from the input via the core formula
# ---------------------------------------------------------------
projected_balances = list(standard_balances)
if has_anchor:
    projected_balances[anchor_idx] = float(anchor_balance)
    prev = float(anchor_balance)
    for i in range(anchor_idx + 1, 24):
        prev = project_month(prev, obligations_per_month[i], float(salary), float(spend_limit))
        projected_balances[i] = prev

# ---------------------------------------------------------------
# Health analysis
# ---------------------------------------------------------------
if has_anchor:
    standard_now = standard_balances[anchor_idx]
    diff_now = float(anchor_balance) - standard_now
    ref_now = max(abs(standard_now), 1.0)
    pct_now = diff_now / ref_now * 100.0
    status_now = zone_of(diff_now, ref_now)

    end_ext = projected_balances[23]
    end_std = standard_balances[23]
    end_diff = end_ext - end_std
    end_ref = max(abs(end_std), 1.0)
    end_pct = end_diff / end_ref * 100.0

    path = projected_balances[anchor_idx:]
    path_min = min(path)
    path_min_i = anchor_idx + path.index(path_min)

    status_traj = "red" if path_min < 0 else zone_of(end_diff, end_ref)
else:
    status_now = status_traj = "info"

SEVERITY = {"green": 0, "amber": 1, "red": 2}

# ---------------------------------------------------------------
# AI Financial Coach
# ---------------------------------------------------------------
if status_now == "info":
    banner_class = "coach-info"
    body = (
        "👋 أهلًا بك! حدّد شهرك الحالي وأدخل رصيدك الفعلي في بطاقة «تحديث الوضع الحالي» بالأعلى، "
        "وسأعيد فورًا رسم توقعات الأشهر القادمة وأخبرك إلى أين يقودك مسارك."
    )
    traj_html = ""
else:
    if status_now == "green":
        body = (
            f"🎉 عمل رائع! في <b>{month_labels[anchor_idx]}</b> أنت متقدم على الخطة الأصلية بنسبة "
            f"<b>{abs(pct_now):.1f}%</b> (+{fmt(diff_now)} {currency})."
        )
    elif status_now == "amber":
        body = (
            f"⚠️ انتبه! في <b>{month_labels[anchor_idx]}</b> رصيدك أدنى من الخطة الأصلية بمقدار "
            f"<b>{fmt(abs(diff_now))} {currency}</b> ({abs(pct_now):.1f}%). أنت في منطقة الحذر."
        )
    else:
        daily_cut = abs(diff_now) / 30.0
        body = (
            f"🚨 تحذير: في <b>{month_labels[anchor_idx]}</b> أنت داخل المنطقة غير المريحة بمقدار "
            f"<b>{fmt(abs(diff_now))} {currency}</b> ({abs(pct_now):.1f}% تحت الهدف). "
            f"قلّل صرفك اليومي بحوالي <b>{fmt(daily_cut)} {currency}</b>."
        )

    if status_traj == "red" and path_min < 0:
        traj_line = (
            f"🔮 <b>المسار المستقبلي:</b> على هذا الوضع، يُتوقع أن يهبط رصيدك إلى "
            f"<b>{fmt(path_min)} {currency}</b> في <b>{month_labels[path_min_i]}</b> — عجز فعلي. "
            f"خفّض الصرف الآن قبل الوصول لتلك المحطة."
        )
    elif status_traj == "red":
        traj_line = (
            f"🔮 <b>المسار المستقبلي:</b> توقعك لنهاية الخطة (<b>{fmt(end_ext)} {currency}</b>) "
            f"أدنى بكثير من الهدف الأصلي (<b>{fmt(end_std)} {currency}</b>) بفارق {fmt(abs(end_diff))} {currency}."
        )
    elif status_traj == "amber":
        traj_line = (
            f"🔮 <b>المسار المستقبلي:</b> مسارك ينحرف قليلًا — متوقع أن تنهي الخطة عند "
            f"<b>{fmt(end_ext)} {currency}</b> مقابل هدف <b>{fmt(end_std)} {currency}</b> "
            f"({abs(end_pct):.1f}% أدنى). انحراف قابل للتصحيح بسهولة."
        )
    else:
        traj_line = (
            f"🔮 <b>المسار المستقبلي:</b> ممتاز — توقعك لنهاية الخطة "
            f"<b>{fmt(end_ext)} {currency}</b> يساوي أو يتجاوز الهدف الأصلي ({fmt(end_std)} {currency})."
        )
    traj_html = f'<div class="coach-traj">{traj_line}</div>'

    worst = status_now if SEVERITY[status_now] >= SEVERITY[status_traj] else status_traj
    banner_class = {"green": "coach-green", "amber": "coach-amber", "red": "coach-red"}[worst]

st.markdown(
    f'<div class="coach-box {banner_class}">'
    f'<div class="coach-title">🤖 مدربك المالي الذكي</div>{body}{traj_html}</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# SINGLE health gauge — the final destination (Month 24 forecast)
# ---------------------------------------------------------------
if has_anchor:
    ref = max(abs(end_std), 1.0)
    lo = min(0.0, end_ext, end_std)
    hi = max(end_ext, end_std, 1.0)
    span = max(hi - lo, 1.0)
    rng_min = lo - 0.05 * span
    rng_max = hi + 0.15 * span
    amber_low = end_std - 0.10 * ref  # bottom of the caution zone

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=end_ext,
            number={"valueformat": ",.0f", "suffix": f" {currency}", "font": {"size": 30}},
            delta={"reference": end_std, "valueformat": ",.0f"},
            title={"text": f"🏁 توقع نهاية الخطة — {month_labels[23]}", "font": {"size": 16}},
            gauge={
                "axis": {"range": [rng_min, rng_max], "tickformat": ",.0f"},
                "bar": {"color": "#1f2a44", "thickness": 0.28},
                "steps": [
                    {"range": [rng_min, amber_low], "color": "#ef5350"},
                    {"range": [amber_low, end_std], "color": "#ffca28"},
                    {"range": [end_std, rng_max], "color": "#66bb6a"},
                ],
                "threshold": {
                    "line": {"color": "#1f2a44", "width": 4},
                    "thickness": 0.9,
                    "value": end_std,
                },
            },
        )
    )
    fig.update_layout(
        height=290,
        margin=dict(l=30, r=30, t=70, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Cairo, sans-serif"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Compact metric blocks (wrap on narrow screens)
    now_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_now]
    traj_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_traj]
    diff_sign = "+" if diff_now >= 0 else "−"
    st.markdown(
        f"""
        <div class="metric-row">
          <div class="metric-block mb-blue">
            <div class="metric-label">رصيدك الفعلي — {month_labels[anchor_idx]}</div>
            <div class="metric-value">{fmt(float(anchor_balance))}</div>
          </div>
          <div class="metric-block mb-gray">
            <div class="metric-label">الهدف الأصلي لهذا الشهر</div>
            <div class="metric-value">{fmt(standard_now)}</div>
          </div>
          <div class="metric-block {now_class}">
            <div class="metric-label">الفرق الحالي</div>
            <div class="metric-value">{diff_sign}{fmt(abs(diff_now))}</div>
          </div>
          <div class="metric-block {traj_class}">
            <div class="metric-label">توقع نهاية الخطة</div>
            <div class="metric-value">{fmt(end_ext)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Future milestone cards (upcoming annual obligations)
# ---------------------------------------------------------------
st.markdown('<div class="section-title">🗓️ المحطات القادمة — الالتزامات السنوية</div>', unsafe_allow_html=True)

current_position = (anchor_idx + 1) if has_anchor else 1  # 1-based current month
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
        after_balance = projected_balances[due - 1]
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
# Clean 2-column projection table (read-only, mobile-friendly)
# ---------------------------------------------------------------
st.markdown('<div class="section-title">📋 المسار الشهري المتوقع (24 شهرًا)</div>', unsafe_allow_html=True)
if has_anchor:
    st.caption("الأشهر قبل شهرك الحالي تعرض الخطة الأصلية، وشهرك الحالي وما بعده يعرضان التوقع المحدث من رصيدك الفعلي.")
else:
    st.caption("لم تُدخل رصيدًا فعليًا بعد — الجدول يعرض الخطة المعيارية الأصلية.")

row_labels = []
for i in range(24):
    marker = "  ⬅️ أنت هنا" if (has_anchor and i == anchor_idx) else ""
    row_labels.append(f"{month_labels[i]}{marker}")

table_df = pd.DataFrame(
    {
        "الشهر": row_labels,
        "الرصيد المتوقع المحدث": projected_balances,
    }
)

st.dataframe(
    table_df,
    hide_index=True,
    use_container_width=True,
    height=500,
    column_config={
        "الشهر": st.column_config.TextColumn("الشهر", width="medium"),
        "الرصيد المتوقع المحدث": st.column_config.NumberColumn(
            f"الرصيد المتوقع المحدث ({currency})", format="%.0f"
        ),
    },
)

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.caption(
    "💡 القاعدة: الشهر التالي = (رصيد الشهر السابق − التزامات الشهر) + الراتب − حد الصرف المستهدف. "
    "عند إدخال رصيدك الفعلي يُصبح هو نقطة الانطلاق الجديدة لكل الأشهر القادمة. "
    "تُحفظ اختياراتك طوال الجلسة الحالية."
)
