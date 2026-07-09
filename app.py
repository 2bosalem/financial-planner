# -*- coding: utf-8 -*-
"""
لوحة التخطيط المالي الذكية — Smart Financial Planning Dashboard (v5)
Compact zero-scroll mobile layout:
  * All 4 annual obligations deducted ONCE in month 1 (both scenarios)
  * Continuous formula afterwards: next = (current - spending) + salary
  * Gauge + coach focused on the upcoming month of June (يونيو)
  * Custom compact HTML table (3 columns, centered, anchor row highlighted)
  * Icon-font-safe CSS (no ghost text behind expander headers)
Arabic RTL.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------
# Page configuration
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
JUNE = 5  # index of يونيو in MONTH_NAMES

# ---------------------------------------------------------------
# Global CSS — compact single-screen layout, Arabic RTL, centered numbers.
# NOTE: the Cairo font is applied to text elements only, and the Material
# icon font is explicitly restored afterwards — this fixes the duplicated
# "ghost text" that appeared behind the expander/settings headers.
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    /* Arabic typography — WITHOUT breaking Streamlit's icon fonts */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stApp input, .stApp button, .stApp select, .stApp td, .stApp th {
        font-family: 'Cairo', sans-serif;
    }
    [data-testid="stIconMaterial"],
    span[class*="material-symbols"],
    i[class*="material-icons"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    .stApp { direction: rtl; }
    [data-testid="stNumberInput"] input { direction: ltr; text-align: center; }

    /* Tighten everything vertically for a zero-scroll phone view */
    .block-container { padding-top: 0.8rem; padding-bottom: 0.4rem; }
    [data-testid="stVerticalBlock"] { gap: 0.45rem; }
    header[data-testid="stHeader"] { height: 2rem; background: transparent; }
    label[data-testid="stWidgetLabel"] p { font-size: 0.78rem; margin-bottom: 0; }
    [data-testid="stExpander"] summary p { font-size: 0.85rem; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; }
    [data-testid="stCaptionContainer"] p { font-size: 0.7rem; margin: 0; }

    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.15rem;
        margin: 0;
    }

    /* AI coach — compact banner */
    .coach-box {
        border-radius: 14px;
        padding: 10px 14px;
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 700;
        line-height: 1.7;
        box-shadow: 0 4px 12px rgba(0,0,0,0.14);
        text-align: center;
    }
    .coach-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .coach-amber { background: linear-gradient(135deg, #f7971e, #ffd200); color: #3a2c00; }
    .coach-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .coach-info  { background: linear-gradient(135deg, #2b5876, #4e4376); }

    /* Metric blocks — 2x2 grid on phones, all values centered */
    .metric-row { display: flex; flex-wrap: wrap; gap: 8px; }
    .metric-block {
        flex: 1 1 42%;
        min-width: 120px;
        border-radius: 12px;
        padding: 8px 6px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 3px 9px rgba(0,0,0,0.12);
    }
    .metric-label { font-size: 0.68rem; opacity: 0.92; text-align: center; }
    .metric-value { font-size: 1.0rem; font-weight: 900; direction: ltr; text-align: center; }
    .mb-blue  { background: linear-gradient(135deg, #396afc, #2948ff); }
    .mb-gray  { background: linear-gradient(135deg, #556270, #4ecdc4); }
    .mb-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .mb-amber { background: linear-gradient(135deg, #f7971e, #ffb200); }
    .mb-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }

    /* Compact custom table — centered cells, tight rows, internal scroll */
    .tbl-wrap {
        max-height: 240px;
        overflow-y: auto;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
    }
    table.ftable {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.76rem;
    }
    table.ftable th {
        position: sticky;
        top: 0;
        padding: 5px 6px;
        text-align: center;
        font-weight: 900;
        background: rgba(57,106,252,0.16);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(57,106,252,0.4);
    }
    table.ftable td {
        padding: 3px 6px;
        text-align: center;
        border-bottom: 1px solid rgba(128,128,128,0.10);
    }
    table.ftable td.num { direction: ltr; }
    table.ftable tr:nth-child(even) td { background: rgba(128,128,128,0.05); }
    table.ftable tr.anchor-row td {
        background: rgba(57,106,252,0.24);
        font-weight: 900;
        border-top: 2px solid #396afc;
        border-bottom: 2px solid #396afc;
    }
    table.ftable td.neg { color: #ef473a; font-weight: 900; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt(x: float) -> str:
    """Thousands-separated number, no decimals."""
    return f"{x:,.0f}"


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

# ---------------------------------------------------------------
# Settings + obligations — ONE collapsed expander to save vertical space
# ---------------------------------------------------------------
with st.expander("⚙️ إعدادات الخطة والالتزامات السنوية", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        start_month = st.selectbox(
            "شهر بداية الخطة",
            options=list(range(1, 13)),
            format_func=lambda m: MONTH_NAMES[m - 1],
            index=0,
            key="start_month",
        )
        initial_balance = st.number_input("الرصيد الافتتاحي", value=10000.0, step=500.0, key="init_balance")
        currency = st.text_input("رمز العملة", value="KD", max_chars=8, key="currency")
    with c2:
        start_year = st.number_input("سنة البداية", min_value=2020, max_value=2100, value=2026, step=1, key="start_year")
        salary = st.number_input("الراتب الشهري", min_value=0.0, value=8000.0, step=250.0, key="salary")
        spend_limit = st.number_input("حد الصرف الشهري", min_value=0.0, value=6000.0, step=250.0, key="spend_limit")

    st.caption("الالتزامات السنوية الأربعة — تُخصم بالكامل دفعة واحدة في الشهر الأول من الخطة:")
    default_obligations = [
        ("تأمين السيارة", 3000.0),
        ("رسوم المدارس", 6000.0),
        ("صيانة / إيجار سنوي", 4000.0),
        ("سفر العائلة", 5000.0),
    ]
    oc1, oc2 = st.columns(2)
    obligation_amounts = []
    for i, (d_name, d_amount) in enumerate(default_obligations, start=1):
        col = oc1 if i % 2 == 1 else oc2
        with col:
            st.text_input(f"اسم الالتزام {i}", value=d_name, key=f"ob_name_{i}")
            obligation_amounts.append(
                st.number_input(f"مبلغ الالتزام {i}", min_value=0.0, value=d_amount, step=500.0, key=f"ob_amount_{i}")
            )

total_obligations = float(sum(obligation_amounts))

# ---------------------------------------------------------------
# Timeline labels
# ---------------------------------------------------------------
month_labels = []
month_nums = []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")
    month_nums.append(m)

# ---------------------------------------------------------------
# Scenario 1 — Standard baseline (STATIC)
#   Month 1 : ((initial - ALL obligations) + salary) - spending
#   Month n : ((previous - 0) + salary) - spending
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(24):
    deduction = total_obligations if i == 0 else 0.0
    prev = (prev - deduction) + float(salary) - float(spend_limit)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# "Current Status Update" — anchor inputs (persisted via widget keys)
# ---------------------------------------------------------------
with st.container(border=True):
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
            placeholder="أدخل رصيدك…",
            key="anchor_balance",
        )

has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Scenario 2 — Extrapolated path (DYNAMIC)
#   * before the anchor : baseline
#   * the anchor month  : exactly the user's input
#   * after the anchor  : next = ((current - spending) + salary)
#     (obligations were already cleared in month 1, so none remain)
# ---------------------------------------------------------------
projected_balances = list(standard_balances)
if has_anchor:
    projected_balances[anchor_idx] = float(anchor_balance)
    prev = float(anchor_balance)
    for i in range(anchor_idx + 1, 24):
        prev = (prev - float(spend_limit)) + float(salary)
        projected_balances[i] = prev

# ---------------------------------------------------------------
# Target month: the upcoming يونيو (June) — at/after the anchor month,
# falling back to the last June in the 24-month window.
# ---------------------------------------------------------------
june_ids = [i for i in range(24) if month_nums[i] == JUNE]
base_pos = anchor_idx if has_anchor else 0
target_idx = next((i for i in june_ids if i >= base_pos), june_ids[-1])
target_label = month_labels[target_idx]

# ---------------------------------------------------------------
# Health analysis — current position + June forecast
# ---------------------------------------------------------------
if has_anchor:
    standard_now = standard_balances[anchor_idx]
    diff_now = float(anchor_balance) - standard_now
    ref_now = max(abs(standard_now), 1.0)
    status_now = zone_of(diff_now, ref_now)

    june_proj = projected_balances[target_idx]
    june_std = standard_balances[target_idx]
    june_diff = june_proj - june_std
    june_ref = max(abs(june_std), 1.0)
    june_pct = june_diff / june_ref * 100.0

    path = projected_balances[anchor_idx: target_idx + 1]
    path_min = min(path)
    status_june = "red" if path_min < 0 else zone_of(june_diff, june_ref)
else:
    status_now = status_june = "info"

SEVERITY = {"green": 0, "amber": 1, "red": 2}

# ---------------------------------------------------------------
# AI Financial Coach — one compact banner focused on June
# ---------------------------------------------------------------
if status_now == "info":
    banner_class = "coach-info"
    msg = "👋 اختر شهرك الحالي وأدخل رصيدك الفعلي بالأعلى — وسأتوقع فورًا وضعك في يونيو القادم."
else:
    if status_june == "red" and path_min < 0:
        msg = (
            f"🚨 تحذير: مسارك الحالي يقودك إلى عجز قبل <b>{target_label}</b> "
            f"(أدنى نقطة: {fmt(path_min)} {currency}). قلّل الصرف فورًا."
        )
    elif status_june == "red":
        msg = (
            f"🚨 توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} — "
            f"أدنى من الهدف ({fmt(june_std)}) بمقدار {fmt(abs(june_diff))} ({abs(june_pct):.0f}%). خفّض صرفك اليومي."
        )
    elif status_june == "amber":
        msg = (
            f"⚠️ توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} مقابل هدف {fmt(june_std)} — "
            f"انحراف {abs(june_pct):.0f}% قابل للتصحيح. راقب مصروفك."
        )
    else:
        msg = (
            f"🎉 ممتاز! توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} — "
            f"يساوي أو يتجاوز هدفك الأصلي ({fmt(june_std)} {currency}). استمر!"
        )
    worst = status_now if SEVERITY[status_now] >= SEVERITY[status_june] else status_june
    banner_class = {"green": "coach-green", "amber": "coach-amber", "red": "coach-red"}[worst]

st.markdown(f'<div class="coach-box {banner_class}">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# Compact gauge — June forecast vs June baseline target
# ---------------------------------------------------------------
if has_anchor:
    lo = min(0.0, june_proj, june_std)
    hi = max(june_proj, june_std, 1.0)
    span = max(hi - lo, 1.0)
    rng_min = lo - 0.05 * span
    rng_max = hi + 0.15 * span
    amber_low = june_std - 0.10 * june_ref

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=june_proj,
            number={"valueformat": ",.0f", "suffix": f" {currency}", "font": {"size": 20}},
            delta={"reference": june_std, "valueformat": ",.0f", "font": {"size": 13}},
            title={"text": f"🎯 توقع {target_label}", "font": {"size": 13}},
            gauge={
                "axis": {"range": [rng_min, rng_max], "tickformat": ",.0f", "tickfont": {"size": 9}},
                "bar": {"color": "#1f2a44", "thickness": 0.30},
                "steps": [
                    {"range": [rng_min, amber_low], "color": "#ef5350"},
                    {"range": [amber_low, june_std], "color": "#ffca28"},
                    {"range": [june_std, rng_max], "color": "#66bb6a"},
                ],
                "threshold": {
                    "line": {"color": "#1f2a44", "width": 3},
                    "thickness": 0.9,
                    "value": june_std,
                },
            },
        )
    )
    fig.update_layout(
        height=175,
        margin=dict(l=15, r=15, t=32, b=2),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Cairo, sans-serif"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "staticPlot": True})

    # Metric blocks — all values centered
    now_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_now]
    june_class = {"green": "mb-green", "amber": "mb-amber", "red": "mb-red"}[status_june]
    diff_sign = "+" if diff_now >= 0 else "−"
    st.markdown(
        f"""
        <div class="metric-row">
          <div class="metric-block mb-blue">
            <div class="metric-label">رصيدك الفعلي الآن</div>
            <div class="metric-value">{fmt(float(anchor_balance))}</div>
          </div>
          <div class="metric-block mb-gray">
            <div class="metric-label">هدف الشهر الأصلي</div>
            <div class="metric-value">{fmt(standard_now)}</div>
          </div>
          <div class="metric-block {now_class}">
            <div class="metric-label">الفرق الحالي</div>
            <div class="metric-value">{diff_sign}{fmt(abs(diff_now))}</div>
          </div>
          <div class="metric-block {june_class}">
            <div class="metric-label">توقع {target_label}</div>
            <div class="metric-value">{fmt(june_proj)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Compact 3-column table: التاريخ | الخطّة الأصلية (KD) | التوقع المحدث (KD)
# Custom HTML for full control: centered cells, tight rows, highlighted
# anchor row, and internal scrolling so the page itself never scrolls.
# ---------------------------------------------------------------
rows_html = ""
for i in range(24):
    row_class = ' class="anchor-row"' if (has_anchor and i == anchor_idx) else ""
    date_cell = f"📍 {month_labels[i]}" if (has_anchor and i == anchor_idx) else month_labels[i]
    std_v, prj_v = standard_balances[i], projected_balances[i]
    std_cls = "num neg" if std_v < 0 else "num"
    prj_cls = "num neg" if prj_v < 0 else "num"
    rows_html += (
        f"<tr{row_class}><td>{date_cell}</td>"
        f'<td class="{std_cls}">{fmt(std_v)}</td>'
        f'<td class="{prj_cls}">{fmt(prj_v)}</td></tr>'
    )

st.markdown(
    f"""
    <div class="tbl-wrap">
      <table class="ftable">
        <thead>
          <tr>
            <th>التاريخ</th>
            <th>الخطّة الأصلية ({currency})</th>
            <th>التوقع المحدث ({currency})</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """,
    unsafe_allow_html=True,
)
