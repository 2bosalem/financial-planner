# -*- coding: utf-8 -*-
"""
منصة الثروة الخاصة — Private Banking Wealth Terminal (v8)
Apple-inspired minimalist rebuild:
  * Native widgets are themed via .streamlit/config.toml (NOT CSS hacks),
    so nothing bleeds or overlaps in any theme.
  * Custom CSS styles ONLY self-contained HTML blocks (status line,
    May Target Terminal, data table) — strict block separation.
  * الخطة المحدثة shows '—' for every month BEFORE the selected current
    month; it anchors strictly at the entered actual balance.
  * Total annual obligations = fixed structural hit in Month 1 for BOTH
    chains; continuous formula: next = ((current − spending) + salary).
Arabic RTL, zero-scroll, two balanced zones.
"""

import streamlit as st

# ---------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="منصة الثروة الخاصة",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MONTH_NAMES = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]
MAY = 4  # index of مايو

# ---------------------------------------------------------------
# Minimal, surgical CSS — Apple private-banking aesthetic.
# Rules touch ONLY: typography, spacing, and self-contained custom
# HTML blocks. Native widget surfaces are left to the Streamlit theme
# (.streamlit/config.toml) so there is zero text/background bleed.
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    /* Typography — icon-font safe */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stApp input, .stApp button, .stApp td, .stApp th {
        font-family: 'Tajawal', -apple-system, system-ui, sans-serif;
    }
    [data-testid="stIconMaterial"],
    span[class*="material-symbols"],
    i[class*="material-icons"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* RTL + compact spacing (layout only — no colors, no surfaces) */
    .stApp { direction: rtl; }
    .block-container { padding-top: 0.7rem; padding-bottom: 0.4rem; max-width: 1150px; }
    [data-testid="stVerticalBlock"] { gap: 0.45rem; }
    [data-testid="stHorizontalBlock"] { gap: 0.9rem; }
    header[data-testid="stHeader"] { height: 1.5rem; background: transparent; }
    label[data-testid="stWidgetLabel"] p { font-size: 0.74rem; font-weight: 700; }
    [data-testid="stNumberInput"] input { direction: ltr; text-align: center; }
    [data-testid="stExpander"] summary p { font-size: 0.78rem; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
    [data-testid="stCaptionContainer"] p { font-size: 0.66rem; margin: 0; }

    /* ---------- Self-contained custom blocks (fixed light palette) ---------- */
    .hero {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 800;
        color: #1d1d1f;
        letter-spacing: 0.3px;
        margin: 0;
    }

    /* Status line — one clean white card, colored dot + text */
    .status-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 16px;
        padding: 9px 14px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: 700;
        color: #1d1d1f;
        line-height: 1.65;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .status-dot {
        display: inline-block;
        width: 9px; height: 9px;
        border-radius: 50%;
        margin-left: 7px;
        vertical-align: 1px;
    }
    .dot-green { background: #34c759; }
    .dot-amber { background: #ff9f0a; }
    .dot-red   { background: #ff3b30; }
    .dot-info  { background: #0a84ff; }
    .status-strong { font-weight: 800; }
    .t-green { color: #248a3d; }
    .t-amber { color: #c67b00; }
    .t-red   { color: #d70015; }

    /* May Target Terminal — isolated, centered grid */
    .may-terminal {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 16px;
        padding: 10px 12px 9px 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .may-terminal-title {
        text-align: center;
        font-size: 0.72rem;
        font-weight: 800;
        color: #86868b;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .may-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    .may-cell {
        text-align: center;
        border: 1px solid #f0f0f2;
        border-radius: 14px;
        padding: 8px 4px;
        background: linear-gradient(180deg, #ffffff, #fbfaf7);
    }
    .may-year {
        font-size: 0.78rem;
        font-weight: 800;
        color: #1d1d1f;
        margin-bottom: 5px;
    }
    .may-pair {
        display: flex;
        justify-content: center;
        gap: 14px;
    }
    .may-item { min-width: 74px; }
    .may-k { font-size: 0.6rem; color: #86868b; font-weight: 700; }
    .may-v {
        font-size: 0.98rem;
        font-weight: 800;
        color: #1d1d1f;
        direction: ltr;
        text-align: center;
    }
    .may-v.pos { color: #248a3d; }
    .may-v.neg { color: #d70015; }
    .may-v.mut { color: #c7c7cc; }
    .delta-chip {
        display: inline-block;
        margin-top: 5px;
        direction: ltr;
        font-size: 0.64rem;
        font-weight: 800;
        padding: 1px 10px;
        border-radius: 999px;
    }
    .chip-pos { background: rgba(52,199,89,0.12); color: #248a3d; }
    .chip-neg { background: rgba(255,59,48,0.10); color: #d70015; }
    .chip-mut { background: #f2f2f7; color: #86868b; }

    /* Data table — hairline separators, centered, internal scroll */
    .tbl-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        max-height: 300px;
        overflow-y: auto;
    }
    table.wtable { width: 100%; border-collapse: collapse; font-size: 0.74rem; }
    table.wtable th {
        position: sticky; top: 0; z-index: 1;
        background: #ffffff;
        color: #86868b;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.4px;
        padding: 7px 6px 5px 6px;
        text-align: center;
        border-bottom: 1px solid #e5e5ea;
    }
    table.wtable td {
        padding: 4px 6px;
        text-align: center;
        color: #1d1d1f;
        border-bottom: 1px solid #f2f2f7;
    }
    table.wtable td.num { direction: ltr; font-weight: 700; }
    table.wtable td.mut { color: #c7c7cc; font-weight: 400; }
    table.wtable td.neg { color: #d70015; font-weight: 800; }

    /* May milestone rows — champagne gold tint, heavy weight */
    table.wtable tr.may-row td {
        background: rgba(212, 175, 55, 0.10);
        font-weight: 800;
        border-top: 1px solid rgba(212, 175, 55, 0.35);
        border-bottom: 1px solid rgba(212, 175, 55, 0.35);
    }

    /* Anchor (current month) row — declared last so it wins */
    table.wtable tr.anchor-row td {
        background: rgba(10, 132, 255, 0.08);
        font-weight: 800;
        border-top: 1.5px solid #0a84ff;
        border-bottom: 1.5px solid #0a84ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt(x: float) -> str:
    """Thousands-separated number, no decimals."""
    return f"{x:,.0f}"


# ---------------------------------------------------------------
# Header + status placeholder (filled after inputs are read)
# ---------------------------------------------------------------
st.markdown('<div class="hero">🏦 منصة الثروة الخاصة</div>', unsafe_allow_html=True)
status_area = st.container()

# ===============================================================
# TWO BALANCED ZONES: [inputs | May targets + table]
# ===============================================================
zone_inputs, zone_results = st.columns([1, 1])

# ---------------------------------------------------------------
# ZONE 1 — Inputs
# ---------------------------------------------------------------
with zone_inputs:
    with st.container(border=True):
        st.caption("تحديث الوضع الحالي")
        _sm = st.session_state.get("start_month", 1)
        _sy = st.session_state.get("start_year", 2026)
        _labels = []
        for i in range(24):
            m = (_sm - 1 + i) % 12
            y = int(_sy) + (_sm - 1 + i) // 12
            _labels.append(f"{MONTH_NAMES[m]} {y}")
        anchor_idx = st.selectbox(
            "الشهر الحالي",
            options=list(range(24)),
            format_func=lambda i: f"{i + 1} — {_labels[i]}",
            index=0,
            key="anchor_month_idx",
        )
        anchor_balance = st.number_input(
            "الرصيد الفعلي الحالي",
            value=None,
            step=500.0,
            placeholder="أدخل رصيدك الحقيقي…",
            key="anchor_balance",
        )

    with st.expander("الإعدادات الأساسية", expanded=False):
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

    with st.expander("الالتزامات السنوية — خصم هيكلي في الشهر الأول", expanded=False):
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
# Chain 1 — الخطة الأصلية (baseline)
#   Month 1: ((initial − TOTAL obligations) − spending) + salary
#   Month n: ((previous − spending) + salary)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(24):
    structural_hit = total_obligations if i == 0 else 0.0
    prev = ((prev - structural_hit) - float(spend_limit)) + float(salary)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — الخطة المحدثة (anchored forecast)
#   * months BEFORE the anchor : None  →  rendered as '—'
#   * anchor month             : the entered actual balance
#     (minus the Month-1 structural obligations hit if the anchor IS month 1,
#      so both chains carry the identical structural deduction)
#   * months AFTER the anchor  : ((previous − spending) + salary)
# ---------------------------------------------------------------
updated_balances = [None] * 24
if has_anchor:
    start_val = float(anchor_balance) - (total_obligations if anchor_idx == 0 else 0.0)
    updated_balances[anchor_idx] = start_val
    prev = start_val
    for i in range(anchor_idx + 1, 24):
        prev = (prev - float(spend_limit)) + float(salary)
        updated_balances[i] = prev

# ---------------------------------------------------------------
# May milestones + focal May (next مايو at/after the anchor)
# ---------------------------------------------------------------
may_ids = [i for i in range(24) if month_nums[i] == MAY]
base_pos = anchor_idx if has_anchor else 0
target_idx = next((i for i in may_ids if i >= base_pos), may_ids[-1])
target_label = month_labels[target_idx]

# ---------------------------------------------------------------
# Status line (top) — calm, one sentence, Apple tone
# ---------------------------------------------------------------
with status_area:
    if not has_anchor or updated_balances[target_idx] is None:
        dot, text = "dot-info", (
            "أدخل شهرك الحالي ورصيدك الفعلي لبدء التتبع — ستُبنى الخطة المحدثة من رصيدك مباشرة حتى محطة مايو."
        )
    else:
        m_std = standard_balances[target_idx]
        m_upd = updated_balances[target_idx]
        m_delta = m_upd - m_std
        path_min = min(v for v in updated_balances[anchor_idx: target_idx + 1] if v is not None)
        if path_min < 0:
            dot = "dot-red"
            text = (
                f'مسارك الحالي يكسر الصفر قبل <span class="status-strong t-red">{target_label}</span> '
                f'(أدنى نقطة {fmt(path_min)} {currency}) — خفّض الإنفاق الآن.'
            )
        elif m_delta >= 0:
            dot = "dot-green"
            text = (
                f'أنت على المسار الصحيح — متوقع أن تبلغ <span class="status-strong">{fmt(m_upd)} {currency}</span> '
                f'في {target_label}، بفائض <span class="status-strong t-green">+{fmt(m_delta)}</span> عن الخطة الأصلية.'
            )
        elif abs(m_delta) <= 0.10 * max(abs(m_std), 1.0):
            dot = "dot-amber"
            text = (
                f'انحراف بسيط — متوقع {fmt(m_upd)} {currency} في {target_label} '
                f'مقابل خطة {fmt(m_std)} (<span class="status-strong t-amber">−{fmt(abs(m_delta))}</span>). قابل للتصحيح.'
            )
        else:
            dot = "dot-red"
            text = (
                f'تراجع واضح — متوقع {fmt(m_upd)} {currency} في {target_label} '
                f'مقابل خطة {fmt(m_std)} (<span class="status-strong t-red">−{fmt(abs(m_delta))}</span>). قلّل الصرف اليومي.'
            )
    st.markdown(
        f'<div class="status-card"><span class="status-dot {dot}"></span>{text}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# ZONE 2 — May Target Terminal + 3-column table
# ---------------------------------------------------------------
with zone_results:
    # --- May Target Terminal (منصة أهداف مايو) ---
    cells = ""
    for mi in may_ids:
        std_v = standard_balances[mi]
        upd_v = updated_balances[mi]
        std_cls = "neg" if std_v < 0 else ""
        if upd_v is None:
            upd_html = '<div class="may-v mut">—</div>'
            chip = '<span class="delta-chip chip-mut">بانتظار التحديث</span>'
        else:
            upd_cls = "neg" if upd_v < 0 else "pos"
            upd_html = f'<div class="may-v {upd_cls}">{fmt(upd_v)}</div>'
            delta = upd_v - std_v
            if delta >= 0:
                chip = f'<span class="delta-chip chip-pos">فائض +{fmt(delta)} {currency}</span>'
            else:
                chip = f'<span class="delta-chip chip-neg">عجز −{fmt(abs(delta))} {currency}</span>'
        cells += f"""
        <div class="may-cell">
          <div class="may-year">مايو {month_labels[mi].split()[-1]}</div>
          <div class="may-pair">
            <div class="may-item">
              <div class="may-k">الخطة الأصلية</div>
              <div class="may-v {std_cls}">{fmt(std_v)}</div>
            </div>
            <div class="may-item">
              <div class="may-k">الخطة المحدثة</div>
              {upd_html}
            </div>
          </div>
          {chip}
        </div>"""

    st.markdown(
        f"""
        <div class="may-terminal">
          <div class="may-terminal-title">منصة أهداف مايو — MAY TARGETS</div>
          <div class="may-grid">{cells}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 3-column table: التاريخ | الخطة الأصلية | الخطة المحدثة ---
    rows = ""
    for i in range(24):
        classes = []
        if month_nums[i] == MAY:
            classes.append("may-row")
        if has_anchor and i == anchor_idx:
            classes.append("anchor-row")
        row_cls = f' class="{" ".join(classes)}"' if classes else ""

        if has_anchor and i == anchor_idx:
            date_cell = f"📍 {month_labels[i]}"
        elif month_nums[i] == MAY:
            date_cell = f"★ {month_labels[i]}"
        else:
            date_cell = month_labels[i]

        std_v = standard_balances[i]
        std_td = f'<td class="num neg">{fmt(std_v)}</td>' if std_v < 0 else f'<td class="num">{fmt(std_v)}</td>'

        upd_v = updated_balances[i]
        if upd_v is None:
            upd_td = '<td class="mut">—</td>'
        elif upd_v < 0:
            upd_td = f'<td class="num neg">{fmt(upd_v)}</td>'
        else:
            upd_td = f'<td class="num">{fmt(upd_v)}</td>'

        rows += f"<tr{row_cls}><td>{date_cell}</td>{std_td}{upd_td}</tr>"

    st.markdown(
        f"""
        <div class="tbl-card">
          <table class="wtable">
            <thead>
              <tr>
                <th>التاريخ</th>
                <th>الخطة الأصلية ({currency})</th>
                <th>الخطة المحدثة ({currency})</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if has_anchor and anchor_idx == 0:
        st.caption(
            f"خُصم إجمالي الالتزامات ({fmt(total_obligations)} {currency}) كخصم هيكلي في الشهر الأول من كلا الخطتين."
        )
