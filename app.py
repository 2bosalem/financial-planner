# -*- coding: utf-8 -*-
"""
لوحة الثروة الشخصية — Luxury Personal Wealth Terminal (v7)
Premium fintech aesthetic, May-focused milestones:
  * "May Milestones" geometric console: side-by-side الخطة الأصلية vs
    التوقع المحدث for every مايو in the 24-month window, with delta pills
  * May rows in the table styled with a luxury gold/emerald tint
  * Full luxury CSS overhaul: ivory background, white 16px-radius cards,
    charcoal secondary text, bold colored financial figures, centered
  * Math unchanged from v6: total obligations deducted instantly from BOTH
    starting points (initial balance AND entered actual balance), then
    next = ((current - spending) + salary)
Arabic RTL, zero-scroll split layout.
"""

import streamlit as st

# ---------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="لوحة الثروة الشخصية",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MONTH_NAMES = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]
MAY = 4  # index of مايو in MONTH_NAMES

# Palette (defined in the CSS below): ivory canvas #f8f7f3, white cards,
# charcoal text #2b2f36, navy #1f2a44, gold #b08d2a, emerald #0f9b6c

# ---------------------------------------------------------------
# Luxury fintech CSS — forced light "wealth terminal" theme,
# centered typography, compact zero-scroll spacing, icon-font safe.
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    /* ---------- Typography (icon-font safe) ---------- */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stApp input, .stApp button, .stApp select, .stApp td, .stApp th {
        font-family: 'Cairo', sans-serif;
    }
    [data-testid="stIconMaterial"],
    span[class*="material-symbols"],
    i[class*="material-icons"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* ---------- Luxury canvas ---------- */
    .stApp {
        direction: rtl;
        background: linear-gradient(180deg, #f8f7f3 0%, #eef0f4 100%);
    }
    .stApp p, .stApp label { color: #2b2f36; }
    header[data-testid="stHeader"] { height: 1.4rem; background: transparent; }
    .block-container { padding-top: 0.5rem; padding-bottom: 0.3rem; max-width: 1180px; }
    [data-testid="stVerticalBlock"] { gap: 0.35rem; }
    [data-testid="stHorizontalBlock"] { gap: 0.7rem; }
    [data-testid="stCaptionContainer"] p { font-size: 0.64rem; margin: 0; color: #6c7280; text-align: center; }

    /* ---------- Inputs: white, rounded, centered ---------- */
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.7rem; font-weight: 700; margin-bottom: 0; text-align: center; width: 100%;
    }
    [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {
        background: #ffffff; color: #1f2a44; font-weight: 700;
        text-align: center; direction: ltr;
        border-radius: 12px; padding: 0.2rem 0.3rem;
    }
    [data-testid="stNumberInput"] > div, [data-testid="stTextInput"] > div > div {
        border-radius: 12px; border-color: #e3e1d8;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #ffffff; color: #1f2a44; font-weight: 700;
        border-radius: 12px; border-color: #e3e1d8; min-height: 2rem;
    }

    /* ---------- Cards: white, soft borders, gentle depth ---------- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid #e6e4dd !important;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(31, 42, 68, 0.06);
    }
    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e6e4dd;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(31, 42, 68, 0.05);
    }
    [data-testid="stExpander"] summary { padding: 0.35rem 0.7rem; }
    [data-testid="stExpander"] summary p { font-size: 0.76rem; font-weight: 900; color: #1f2a44; }

    /* ---------- Header ---------- */
    .app-title {
        text-align: center; font-weight: 900; font-size: 1.12rem;
        color: #1f2a44; margin: 0; letter-spacing: 0.2px;
    }
    .panel-title {
        font-weight: 900; font-size: 0.8rem; color: #1f2a44;
        margin: 0 0 2px 0; text-align: center;
    }

    /* ---------- Coach strip ---------- */
    .coach-box {
        border-radius: 14px; padding: 7px 12px; color: #ffffff;
        font-size: 0.78rem; font-weight: 700; line-height: 1.6;
        box-shadow: 0 4px 14px rgba(31, 42, 68, 0.14); text-align: center;
    }
    .stApp .coach-box, .stApp .coach-box b { color: #ffffff; }
    .coach-amber, .stApp .coach-amber, .stApp .coach-amber b { color: #3a2c00; }
    .coach-green { background: linear-gradient(135deg, #0f9b6c, #2fd58a); }
    .coach-amber { background: linear-gradient(135deg, #e8b62a, #ffd873); }
    .coach-red   { background: linear-gradient(135deg, #b02836, #e5484d); }
    .coach-info  { background: linear-gradient(135deg, #1f2a44, #3d4d78); }

    /* ---------- "May Milestones" geometric console ---------- */
    .may-row { display: flex; gap: 10px; }
    .may-card {
        flex: 1; background: #ffffff; text-align: center;
        border: 1px solid rgba(176, 141, 42, 0.45);
        border-radius: 16px; padding: 8px 6px 7px 6px;
        box-shadow: 0 6px 16px rgba(176, 141, 42, 0.10);
    }
    .may-title {
        font-size: 0.74rem; font-weight: 900; color: #b08d2a;
        letter-spacing: 0.4px; margin-bottom: 3px;
    }
    .may-cols { display: flex; align-items: stretch; }
    .may-col { flex: 1; }
    .may-divider { width: 1px; background: #eceade; margin: 2px 6px; }
    .may-lbl { font-size: 0.6rem; color: #6c7280; font-weight: 700; }
    .may-val {
        font-size: 1.02rem; font-weight: 900; direction: ltr; text-align: center;
    }
    .v-navy { color: #1f2a44; }
    .v-emerald { color: #0f9b6c; }
    .v-red { color: #c92a3b; }
    .may-delta {
        display: inline-block; margin-top: 3px; direction: ltr;
        font-size: 0.66rem; font-weight: 900;
        padding: 1px 10px; border-radius: 999px;
    }
    .d-pos { background: rgba(15, 155, 108, 0.13); color: #0f9b6c; }
    .d-neg { background: rgba(201, 42, 59, 0.12); color: #c92a3b; }

    /* ---------- Table: centered, luxury tints, internal scroll ---------- */
    .tbl-wrap {
        max-height: 285px; overflow-y: auto;
        background: #ffffff;
        border: 1px solid #e6e4dd; border-radius: 16px;
        box-shadow: 0 6px 18px rgba(31, 42, 68, 0.06);
    }
    table.ftable { width: 100%; border-collapse: collapse; font-size: 0.73rem; }
    table.ftable th {
        position: sticky; top: 0; padding: 5px 6px;
        text-align: center; font-weight: 900; color: #1f2a44;
        background: #f4f2ea;
        border-bottom: 1px solid #e3ddc9;
    }
    table.ftable td {
        padding: 2px 6px; text-align: center; color: #2b2f36;
        border-bottom: 1px solid #f0efe9;
    }
    table.ftable td.num { direction: ltr; font-weight: 700; color: #1f2a44; }
    table.ftable tr:nth-child(even) td { background: #fafaf7; }

    /* May milestone rows — luxury gold/emerald tint, heavy bold */
    table.ftable tr.may-row-tint td {
        background: linear-gradient(90deg, rgba(176,141,42,0.16), rgba(15,155,108,0.12));
        font-weight: 900; color: #7a6114;
        border-top: 1px solid rgba(176,141,42,0.45);
        border-bottom: 1px solid rgba(176,141,42,0.45);
    }
    table.ftable tr.may-row-tint td.num { color: #7a6114; }

    /* Anchor (current month) row — declared after May so it wins */
    table.ftable tr.anchor-row td {
        background: rgba(57, 106, 252, 0.16);
        font-weight: 900; color: #1f2a44;
        border-top: 2px solid #396afc; border-bottom: 2px solid #396afc;
    }
    table.ftable tr.anchor-row td.num { color: #1f2a44; }
    table.ftable td.neg, table.ftable tr td.neg { color: #c92a3b !important; font-weight: 900; }
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
# Header + coach placeholder
# ---------------------------------------------------------------
st.markdown('<div class="app-title">💎 لوحة الثروة الشخصية</div>', unsafe_allow_html=True)
coach_area = st.container()

# ===============================================================
# SPLIT LAYOUT: [control panel | results & analytics]
# ===============================================================
panel_col, results_col = st.columns([1, 1.25])

# ---------------------------------------------------------------
# COLUMN 1 — Control panel
# ---------------------------------------------------------------
with panel_col:
    with st.container(border=True):
        st.markdown('<div class="panel-title">🧭 تحديث الوضع الحالي</div>', unsafe_allow_html=True)
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
# Timeline
# ---------------------------------------------------------------
month_labels, month_nums = [], []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")
    month_nums.append(m)

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية: start = initial − TOTAL obligations,
# then next = ((current − spending) + salary)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance) - total_obligations
for i in range(24):
    prev = (prev - float(spend_limit)) + float(salary)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — التوقع المحدث: anchor = entered actual − TOTAL obligations,
# then next = ((current − spending) + salary); baseline before the anchor
# ---------------------------------------------------------------
projected_balances = list(standard_balances)
if has_anchor:
    anchor_net = float(anchor_balance) - total_obligations
    projected_balances[anchor_idx] = anchor_net
    prev = anchor_net
    for i in range(anchor_idx + 1, 24):
        prev = (prev - float(spend_limit)) + float(salary)
        projected_balances[i] = prev

# ---------------------------------------------------------------
# May milestones — every مايو in the window; the focal target is the
# next May at/after the anchor (fallback: last May)
# ---------------------------------------------------------------
may_ids = [i for i in range(24) if month_nums[i] == MAY]
base_pos = anchor_idx if has_anchor else 0
target_idx = next((i for i in may_ids if i >= base_pos), may_ids[-1])
target_label = month_labels[target_idx]

may_proj = projected_balances[target_idx]
may_std = standard_balances[target_idx]
may_diff = may_proj - may_std
may_ref = max(abs(may_std), 1.0)
may_pct = may_diff / may_ref * 100.0

if has_anchor:
    path_min = min(projected_balances[anchor_idx: target_idx + 1])
    status_may = "red" if path_min < 0 else zone_of(may_diff, may_ref)
else:
    path_min = None
    status_may = "info"

# ---------------------------------------------------------------
# Coach strip — May-focused
# ---------------------------------------------------------------
with coach_area:
    if status_may == "info":
        cls, msg = "coach-info", "👋 أدخل شهرك الحالي ورصيدك الفعلي — يُخصم إجمالي الالتزامات فورًا ويُعاد رسم مسارك حتى محطة مايو القادمة."
    elif status_may == "red" and path_min is not None and path_min < 0:
        cls, msg = "coach-red", (
            f"🚨 مسارك يقودك إلى عجز قبل <b>{target_label}</b> (أدنى نقطة: {fmt(path_min)} {currency}). قلّل الصرف فورًا."
        )
    elif status_may == "red":
        cls, msg = "coach-red", (
            f"🚨 توقع <b>{target_label}</b>: {fmt(may_proj)} {currency} — أدنى من الهدف ({fmt(may_std)}) "
            f"بمقدار {fmt(abs(may_diff))} ({abs(may_pct):.0f}%). خفّض صرفك اليومي."
        )
    elif status_may == "amber":
        cls, msg = "coach-amber", (
            f"⚠️ توقع <b>{target_label}</b>: {fmt(may_proj)} {currency} مقابل هدف {fmt(may_std)} — "
            f"انحراف {abs(may_pct):.0f}% قابل للتصحيح."
        )
    else:
        cls, msg = "coach-green", (
            f"🎉 ممتاز! توقع <b>{target_label}</b>: {fmt(may_proj)} {currency} — يساوي أو يتجاوز الهدف ({fmt(may_std)})."
        )
    st.markdown(f'<div class="coach-box {cls}">🤖 {msg}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# COLUMN 2 — Results & analytics
# ---------------------------------------------------------------
with results_col:
    # --- "May Milestones" geometric console (one card per مايو) ---
    cards = ""
    for mi in may_ids:
        std_v = standard_balances[mi]
        prj_v = projected_balances[mi]
        delta = prj_v - std_v
        d_cls = "d-pos" if delta >= 0 else "d-neg"
        d_arrow = "▲" if delta >= 0 else "▼"
        prj_color = "v-red" if prj_v < 0 else "v-emerald"
        std_color = "v-red" if std_v < 0 else "v-navy"
        cards += f"""
        <div class="may-card">
          <div class="may-title">🏛️ {month_labels[mi]}</div>
          <div class="may-cols">
            <div class="may-col">
              <div class="may-lbl">الخطة الأصلية</div>
              <div class="may-val {std_color}">{fmt(std_v)}</div>
            </div>
            <div class="may-divider"></div>
            <div class="may-col">
              <div class="may-lbl">التوقع المحدث</div>
              <div class="may-val {prj_color}">{fmt(prj_v)}</div>
            </div>
          </div>
          <div class="may-delta {d_cls}">{d_arrow} {'+' if delta >= 0 else '−'}{fmt(abs(delta))} {currency}</div>
        </div>"""
    st.markdown(f'<div class="may-row">{cards}</div>', unsafe_allow_html=True)

    if has_anchor:
        st.caption(
            f"خُصم إجمالي الالتزامات ({fmt(total_obligations)} {currency}) فورًا من رصيدك المدخل "
            f"({fmt(float(anchor_balance))}) — رصيد الانطلاق الصافي: {fmt(float(anchor_balance) - total_obligations)} {currency}"
        )

    # --- 3-column table with May tint + anchor highlight ---
    rows_html = ""
    for i in range(24):
        classes = []
        if month_nums[i] == MAY:
            classes.append("may-row-tint")
        if has_anchor and i == anchor_idx:
            classes.append("anchor-row")
        row_class = f' class="{" ".join(classes)}"' if classes else ""
        if has_anchor and i == anchor_idx:
            date_cell = f"📍 {month_labels[i]}"
        elif month_nums[i] == MAY:
            date_cell = f"⭐ {month_labels[i]}"
        else:
            date_cell = month_labels[i]
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
