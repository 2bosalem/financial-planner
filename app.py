# -*- coding: utf-8 -*-
"""
لوحة التخطيط المالي الذكية — Smart Financial Planning Dashboard (v6)
Split-screen, no-gauge, zero-scroll layout:
  * Column 1 (control panel): base settings, 4 obligations (name+amount),
    current-month status update
  * Column 2 (results): centered KPI cards + 3-column styled table
Strict math:
  * total obligations deducted INSTANTLY from the starting point of BOTH
    chains — the initial balance (baseline) AND the entered actual balance
    (extrapolation anchor)
  * continuous formula afterwards: next = ((current - spending) + salary)
Arabic RTL.
"""

import streamlit as st

# ---------------------------------------------------------------
# Page configuration — wide so the two columns sit side-by-side
# ---------------------------------------------------------------
st.set_page_config(
    page_title="لوحة التخطيط المالي الذكية",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MONTH_NAMES = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]
JUNE = 5  # index of يونيو in MONTH_NAMES

# ---------------------------------------------------------------
# Global CSS — ultra-compact split layout, centered numbers, RTL,
# icon-font-safe Arabic typography.
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
    [data-testid="stNumberInput"] input { direction: ltr; text-align: center; padding: 0.2rem 0.3rem; }
    [data-testid="stTextInput"] input { text-align: center; padding: 0.2rem 0.3rem; }

    /* Kill vertical waste everywhere */
    .block-container { padding-top: 0.6rem; padding-bottom: 0.3rem; max-width: 1200px; }
    [data-testid="stVerticalBlock"] { gap: 0.35rem; }
    [data-testid="stHorizontalBlock"] { gap: 0.7rem; }
    header[data-testid="stHeader"] { height: 1.6rem; background: transparent; }
    label[data-testid="stWidgetLabel"] p { font-size: 0.72rem; margin-bottom: 0; }
    [data-testid="stExpander"] summary { padding: 0.35rem 0.6rem; }
    [data-testid="stExpander"] summary p { font-size: 0.78rem; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px; }
    [data-testid="stCaptionContainer"] p { font-size: 0.66rem; margin: 0; }
    [data-testid="stSelectbox"] > div > div { min-height: 2rem; }

    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 1.1rem;
        margin: 0;
    }
    .panel-title {
        font-weight: 900;
        font-size: 0.82rem;
        margin: 0 0 2px 0;
    }

    /* Slim AI coach strip */
    .coach-box {
        border-radius: 12px;
        padding: 7px 12px;
        color: #ffffff;
        font-size: 0.8rem;
        font-weight: 700;
        line-height: 1.6;
        box-shadow: 0 3px 10px rgba(0,0,0,0.13);
        text-align: center;
    }
    .coach-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .coach-amber { background: linear-gradient(135deg, #f7971e, #ffd200); color: #3a2c00; }
    .coach-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .coach-info  { background: linear-gradient(135deg, #2b5876, #4e4376); }

    /* KPI cards — 3 across, everything centered */
    .kpi-row { display: flex; gap: 8px; }
    .kpi {
        flex: 1 1 30%;
        border-radius: 12px;
        padding: 8px 4px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 3px 9px rgba(0,0,0,0.12);
    }
    .kpi-label { font-size: 0.66rem; opacity: 0.92; text-align: center; }
    .kpi-value { font-size: 1.0rem; font-weight: 900; direction: ltr; text-align: center; }
    .k-blue  { background: linear-gradient(135deg, #396afc, #2948ff); }
    .k-green { background: linear-gradient(135deg, #0f9b6c, #38ef7d); }
    .k-amber { background: linear-gradient(135deg, #f7971e, #ffb200); }
    .k-red   { background: linear-gradient(135deg, #cb2d3e, #ef473a); }
    .k-gray  { background: linear-gradient(135deg, #556270, #4ecdc4); }

    /* Compact custom table — centered everything, internal scroll */
    .tbl-wrap {
        max-height: 305px;
        overflow-y: auto;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
    }
    table.ftable {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.74rem;
    }
    table.ftable th {
        position: sticky;
        top: 0;
        padding: 4px 6px;
        text-align: center;
        font-weight: 900;
        background: rgba(57,106,252,0.16);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(57,106,252,0.4);
    }
    table.ftable td {
        padding: 2px 6px;
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
# Header + coach placeholder (filled after inputs are read)
# ---------------------------------------------------------------
st.markdown('<div class="app-title">💰 لوحة التخطيط المالي الذكية</div>', unsafe_allow_html=True)
coach_area = st.container()

# ===============================================================
# SPLIT LAYOUT: [control panel | results & analytics]
# ===============================================================
panel_col, results_col = st.columns([1, 1.2])

# ---------------------------------------------------------------
# COLUMN 1 — Control panel
# ---------------------------------------------------------------
with panel_col:
    # --- Current status update (always visible — the daily-use control) ---
    with st.container(border=True):
        st.markdown('<div class="panel-title">🧭 تحديث الوضع الحالي</div>', unsafe_allow_html=True)
        # month labels need start settings; defaults are read from session
        # state via keys, so compute labels after the settings widgets below
        # would be circular — instead read current values with safe defaults.
        _sm = st.session_state.get("start_month", 1)
        _sy = st.session_state.get("start_year", 2026)
        _labels_preview = []
        for i in range(24):
            m = (_sm - 1 + i) % 12
            y = int(_sy) + (_sm - 1 + i) // 12
            _labels_preview.append(f"{MONTH_NAMES[m]} {y}")
        anchor_idx = st.selectbox(
            "الشهر الحالي",
            options=list(range(24)),
            format_func=lambda i: f"{i + 1} — {_labels_preview[i]}",
            index=0,
            key="anchor_month_idx",
        )
        anchor_balance = st.number_input(
            "الرصيد الفعلي الحالي",
            value=None,
            step=500.0,
            placeholder="أدخل رصيدك…",
            key="anchor_balance",
        )

    # --- Base settings (collapsed to keep the panel short) ---
    with st.expander("⚙️ الإعدادات الأساسية", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            start_month = st.selectbox(
                "شهر البداية",
                options=list(range(1, 13)),
                format_func=lambda m: MONTH_NAMES[m - 1],
                index=0,
                key="start_month",
            )
            initial_balance = st.number_input("الرصيد الافتتاحي", value=10000.0, step=500.0, key="init_balance")
            currency = st.text_input("العملة", value="KD", max_chars=8, key="currency")
        with c2:
            start_year = st.number_input("سنة البداية", min_value=2020, max_value=2100, value=2026, step=1, key="start_year")
            salary = st.number_input("الراتب الشهري", min_value=0.0, value=8000.0, step=250.0, key="salary")
            spend_limit = st.number_input("حد الصرف الشهري", min_value=0.0, value=6000.0, step=250.0, key="spend_limit")

    # --- The 4 annual obligations: name + amount only ---
    with st.expander("📌 الالتزامات السنوية (تُخصم فورًا من نقطة البداية)", expanded=False):
        default_obligations = [
            ("تأمين السيارة", 3000.0),
            ("رسوم المدارس", 6000.0),
            ("صيانة / إيجار سنوي", 4000.0),
            ("سفر العائلة", 5000.0),
        ]
        obligation_amounts = []
        for i, (d_name, d_amount) in enumerate(default_obligations, start=1):
            n_col, a_col = st.columns([1.4, 1])
            n_col.text_input(f"الالتزام {i}", value=d_name, key=f"ob_name_{i}")
            obligation_amounts.append(
                a_col.number_input(f"المبلغ {i}", min_value=0.0, value=d_amount, step=500.0, key=f"ob_amount_{i}")
            )

total_obligations = float(sum(obligation_amounts))
has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Timeline labels (final, from the committed settings values)
# ---------------------------------------------------------------
month_labels, month_nums = [], []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")
    month_nums.append(m)

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية (baseline)
#   starting point = initial balance − TOTAL obligations (instant hit)
#   then every month: next = ((current − spending) + salary)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance) - total_obligations   # instant deduction
for i in range(24):
    prev = (prev - float(spend_limit)) + float(salary)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — التوقع المحدث (extrapolation)
#   * months before the anchor : baseline values
#   * anchor month             : entered actual − TOTAL obligations
#                                (the same instant hit applied to the
#                                 new starting point, as specified)
#   * months after the anchor  : next = ((current − spending) + salary)
# ---------------------------------------------------------------
projected_balances = list(standard_balances)
if has_anchor:
    anchor_net = float(anchor_balance) - total_obligations   # instant deduction
    projected_balances[anchor_idx] = anchor_net
    prev = anchor_net
    for i in range(anchor_idx + 1, 24):
        prev = (prev - float(spend_limit)) + float(salary)
        projected_balances[i] = prev

# ---------------------------------------------------------------
# Target month: the upcoming يونيو (June) at/after the anchor,
# falling back to the last June in the window.
# ---------------------------------------------------------------
june_ids = [i for i in range(24) if month_nums[i] == JUNE]
base_pos = anchor_idx if has_anchor else 0
target_idx = next((i for i in june_ids if i >= base_pos), june_ids[-1])
target_label = month_labels[target_idx]

june_proj = projected_balances[target_idx]
june_std = standard_balances[target_idx]
june_diff = june_proj - june_std
june_ref = max(abs(june_std), 1.0)
june_pct = june_diff / june_ref * 100.0

if has_anchor:
    path_min = min(projected_balances[anchor_idx: target_idx + 1])
    status_june = "red" if path_min < 0 else zone_of(june_diff, june_ref)
else:
    path_min = None
    status_june = "info"

# ---------------------------------------------------------------
# Slim coach strip (top of page, one line)
# ---------------------------------------------------------------
with coach_area:
    if status_june == "info":
        cls, msg = "coach-info", "👋 أدخل شهرك الحالي ورصيدك الفعلي في لوحة التحكم — يُخصم إجمالي الالتزامات فورًا ويُعاد توقع مسارك حتى يونيو."
    elif status_june == "red" and path_min is not None and path_min < 0:
        cls, msg = "coach-red", (
            f"🚨 مسارك يقودك إلى عجز قبل <b>{target_label}</b> (أدنى نقطة: {fmt(path_min)} {currency}). قلّل الصرف فورًا."
        )
    elif status_june == "red":
        cls, msg = "coach-red", (
            f"🚨 توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} — أدنى من الهدف ({fmt(june_std)}) "
            f"بمقدار {fmt(abs(june_diff))} ({abs(june_pct):.0f}%). خفّض صرفك اليومي."
        )
    elif status_june == "amber":
        cls, msg = "coach-amber", (
            f"⚠️ توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} مقابل هدف {fmt(june_std)} — "
            f"انحراف {abs(june_pct):.0f}% قابل للتصحيح."
        )
    else:
        cls, msg = "coach-green", (
            f"🎉 ممتاز! توقع <b>{target_label}</b>: {fmt(june_proj)} {currency} — يساوي أو يتجاوز الهدف ({fmt(june_std)})."
        )
    st.markdown(f'<div class="coach-box {cls}">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# COLUMN 2 — Results & analytics
# ---------------------------------------------------------------
with results_col:
    # --- KPI cards (centered values) ---
    june_cls = {"green": "k-green", "amber": "k-amber", "red": "k-red", "info": "k-gray"}[status_june]
    actual_display = fmt(float(anchor_balance)) if has_anchor else "—"
    diff_display = (
        ("+" if june_diff >= 0 else "−") + fmt(abs(june_diff))
    ) if has_anchor else "—"
    diff_cls = june_cls if has_anchor else "k-gray"

    st.markdown(
        f"""
        <div class="kpi-row">
          <div class="kpi {june_cls}">
            <div class="kpi-label">🎯 توقع {target_label}</div>
            <div class="kpi-value">{fmt(june_proj)}</div>
          </div>
          <div class="kpi k-blue">
            <div class="kpi-label">💰 رصيدك الفعلي المدخل</div>
            <div class="kpi-value">{actual_display}</div>
          </div>
          <div class="kpi {diff_cls}">
            <div class="kpi-label">⚖️ الفرق عن هدف يونيو</div>
            <div class="kpi-value">{diff_display}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if has_anchor:
        st.caption(
            f"↙️ خُصم إجمالي الالتزامات ({fmt(total_obligations)} {currency}) فورًا من رصيدك المدخل — "
            f"رصيد الانطلاق الصافي: {fmt(float(anchor_balance) - total_obligations)} {currency}"
        )

    # --- 3-column table: التاريخ | الخطة الأصلية | التوقع المحدث ---
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
                <th>الخطة الأصلية ({currency})</th>
                <th>التوقع المحدث ({currency})</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
