# -*- coding: utf-8 -*-
"""
منصة الثروة الخاصة — Private Banking Wealth Terminal (v9)
Ultra-premium Apple-inspired UI, iPhone-tailored single-column canvas:
  * Secure gate layer — hardcoded access code "2806", centered login
  * Phone-frame layout (max-width 540px) — the May Target Terminal gets
    full executive width; nothing is squished into side columns
  * Isolated rounded cards (14–16px), centered numbers, hairline borders
  * Financial logic IDENTICAL to the approved version:
      - baseline: obligations = structural hit in Month 1
      - الخطة المحدثة: '—' before the anchor; anchors at the entered
        balance (minus the Month-1 hit only when the anchor IS month 1)
      - continuous chain: next = ((current − spending) + salary)
Arabic RTL.
"""

import streamlit as st

# ---------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="منصة الثروة الخاصة",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

MONTH_NAMES = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]
MAY = 4          # index of مايو
ACCESS_CODE = "2806"

# ---------------------------------------------------------------
# Premium CSS — typography, phone-frame canvas, and self-contained
# custom blocks only. Native widget surfaces stay with the Streamlit
# theme (.streamlit/config.toml) so nothing bleeds or overlaps.
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

    /* Phone-frame canvas: one elegant centered column */
    .stApp { direction: rtl; }
    .block-container {
        max-width: 540px;
        padding-top: 0.9rem;
        padding-bottom: 0.6rem;
    }
    [data-testid="stVerticalBlock"] { gap: 0.6rem; }
    [data-testid="stHorizontalBlock"] { gap: 0.7rem; }
    header[data-testid="stHeader"] { height: 1.4rem; background: transparent; }

    /* Widgets: spacing + centered values only (no surface overrides) */
    label[data-testid="stWidgetLabel"] p { font-size: 0.76rem; font-weight: 700; }
    [data-testid="stNumberInput"] input { direction: ltr; text-align: center; font-weight: 700; }
    [data-testid="stTextInput"] input { text-align: center; font-weight: 700; }
    [data-testid="stExpander"] summary p { font-size: 0.8rem; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
    [data-testid="stCaptionContainer"] p { font-size: 0.68rem; margin: 0; text-align: center; }
    .stButton button, .stFormSubmitButton button { border-radius: 12px; font-weight: 800; }

    /* ---------------- Hero ---------------- */
    .hero {
        text-align: center;
        font-size: 1.14rem;
        font-weight: 800;
        color: #1d1d1f;
        letter-spacing: 0.4px;
        margin: 0 0 2px 0;
    }
    .hero-sub {
        text-align: center;
        font-size: 0.68rem;
        font-weight: 700;
        color: #86868b;
        letter-spacing: 2.5px;
        margin: 0 0 4px 0;
    }

    /* ---------------- Secure gate ---------------- */
    .gate-icon { text-align: center; font-size: 2.4rem; margin: 2.2rem 0 0.4rem 0; }
    .gate-title {
        text-align: center; font-size: 1.05rem; font-weight: 800;
        color: #1d1d1f; margin: 0;
    }
    .gate-sub {
        text-align: center; font-size: 0.74rem; color: #86868b;
        margin: 2px 0 10px 0;
    }

    /* ---------------- Status line ---------------- */
    .status-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 16px;
        padding: 12px 16px;
        text-align: center;
        font-size: 0.82rem;
        font-weight: 700;
        color: #1d1d1f;
        line-height: 1.7;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .status-dot {
        display: inline-block; width: 9px; height: 9px;
        border-radius: 50%; margin-left: 8px; vertical-align: 1px;
    }
    .dot-green { background: #34c759; }
    .dot-amber { background: #ff9f0a; }
    .dot-red   { background: #ff3b30; }
    .dot-info  { background: #0a84ff; }
    .status-strong { font-weight: 800; }
    .t-green { color: #248a3d; }
    .t-amber { color: #c67b00; }
    .t-red   { color: #d70015; }

    /* ---------------- May Target Terminal (executive width) ---------------- */
    .may-terminal {
        background: linear-gradient(180deg, #1d1d1f 0%, #2c2c2e 100%);
        border-radius: 16px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.16);
    }
    .may-terminal-title {
        text-align: center;
        font-size: 0.7rem;
        font-weight: 800;
        color: #c9a86a;
        letter-spacing: 3px;
        margin-bottom: 12px;
    }
    .may-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .may-cell {
        text-align: center;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(201,168,106,0.35);
        border-radius: 14px;
        padding: 12px 8px 11px 8px;
    }
    .may-year {
        font-size: 0.86rem; font-weight: 800; color: #f5f5f7;
        margin-bottom: 9px; letter-spacing: 0.4px;
    }
    .may-item { margin-bottom: 7px; }
    .may-k { font-size: 0.62rem; color: #98989d; font-weight: 700; margin-bottom: 1px; }
    .may-v {
        font-size: 1.22rem; font-weight: 800; color: #f5f5f7;
        direction: ltr; text-align: center; line-height: 1.25;
    }
    .may-v.pos { color: #30d158; }
    .may-v.neg { color: #ff453a; }
    .may-v.mut { color: #636366; font-weight: 400; }
    .delta-chip {
        display: inline-block; direction: ltr;
        font-size: 0.68rem; font-weight: 800;
        padding: 2px 12px; border-radius: 999px;
    }
    .chip-pos { background: rgba(48,209,88,0.16); color: #30d158; }
    .chip-neg { background: rgba(255,69,58,0.16); color: #ff453a; }
    .chip-mut { background: rgba(255,255,255,0.08); color: #98989d; }

    /* ---------------- Data table ---------------- */
    .tbl-card {
        background: #ffffff;
        border: 1px solid #e5e5ea;
        border-radius: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        max-height: 258px;
        overflow-y: auto;
    }
    table.wtable { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
    table.wtable th {
        position: sticky; top: 0; z-index: 1;
        background: #ffffff;
        color: #86868b;
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        padding: 9px 6px 7px 6px;
        text-align: center;
        border-bottom: 1px solid #e5e5ea;
    }
    table.wtable td {
        padding: 5.5px 6px;
        text-align: center;
        color: #1d1d1f;
        border-bottom: 1px solid #f2f2f7;
    }
    table.wtable td.num { direction: ltr; font-weight: 700; }
    table.wtable td.mut { color: #c7c7cc; font-weight: 400; }
    table.wtable td.neg { color: #d70015; font-weight: 800; }

    /* May milestone rows — champagne gold, heavy bold */
    table.wtable tr.may-row td {
        background: linear-gradient(90deg, rgba(201,168,106,0.16), rgba(52,199,89,0.08));
        font-weight: 800;
        border-top: 1px solid rgba(201,168,106,0.4);
        border-bottom: 1px solid rgba(201,168,106,0.4);
    }

    /* Anchor row — soft blue, declared last so it wins over May */
    table.wtable tr.anchor-row td {
        background: rgba(10,132,255,0.09);
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


# ===============================================================
# SECURE GATE — access code required before anything renders
# ===============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="gate-icon">🏦</div>', unsafe_allow_html=True)
    st.markdown('<div class="gate-title">منصة الثروة الخاصة</div>', unsafe_allow_html=True)
    st.markdown('<div class="gate-sub">PRIVATE BANKING TERMINAL — أدخل الرمز السري للمتابعة</div>', unsafe_allow_html=True)

    _, gate_col, _ = st.columns([1, 1.4, 1])
    with gate_col:
        with st.form("gate_form", border=False):
            code = st.text_input(
                "الرمز السري",
                type="password",
                placeholder="••••",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("دخول", use_container_width=True)
        if submitted:
            if code == ACCESS_CODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("الرمز غير صحيح — حاول مرة أخرى.")
    st.stop()

# ===============================================================
# MAIN TERMINAL — visual order via placeholders:
#   hero → status → anchor card → May Terminal → table → settings
# (settings are FILLED first in code so their values feed every block,
#  while remaining at the bottom of the page visually)
# ===============================================================
st.markdown('<div class="hero">🏦 منصة الثروة الخاصة</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">PRIVATE WEALTH TERMINAL</div>', unsafe_allow_html=True)

status_area = st.container()
anchor_area = st.container()
terminal_area = st.container()
table_area = st.container()
settings_area = st.container()

# ---------------------------------------------------------------
# Settings (rendered at the bottom visually, executed first)
# ---------------------------------------------------------------
with settings_area:
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

# ---------------------------------------------------------------
# Timeline (real committed settings values — no session-state guessing)
# ---------------------------------------------------------------
month_labels, month_nums = [], []
for i in range(24):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    month_labels.append(f"{MONTH_NAMES[m]} {y}")
    month_nums.append(m)

# ---------------------------------------------------------------
# Anchor inputs (visually right under the status line)
# ---------------------------------------------------------------
with anchor_area:
    with st.container(border=True):
        a1, a2 = st.columns(2)
        with a1:
            anchor_idx = st.selectbox(
                "الشهر الحالي",
                options=list(range(24)),
                format_func=lambda i: f"{i + 1} — {month_labels[i]}",
                index=0,
                key="anchor_month_idx",
            )
        with a2:
            anchor_balance = st.number_input(
                "الرصيد الفعلي الحالي",
                value=None,
                step=500.0,
                placeholder="أدخل رصيدك…",
                key="anchor_balance",
            )

has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية (baseline)  [IDENTICAL approved logic]
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
# Chain 2 — الخطة المحدثة (anchored forecast)  [IDENTICAL approved logic]
#   * months BEFORE the anchor : None → rendered as '—'
#   * anchor month             : entered balance (minus the Month-1
#                                structural hit only when anchor IS month 1)
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
# Status line — calm, one sentence
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
                f'أنت على المسار الصحيح — متوقع <span class="status-strong">{fmt(m_upd)} {currency}</span> '
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
# May Target Terminal — executive dark block, full canvas width
# ---------------------------------------------------------------
with terminal_area:
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
          <div class="may-item">
            <div class="may-k">الخطة الأصلية</div>
            <div class="may-v {std_cls}">{fmt(std_v)}</div>
          </div>
          <div class="may-item">
            <div class="may-k">الخطة المحدثة</div>
            {upd_html}
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

# ---------------------------------------------------------------
# 3-column table: التاريخ | الخطة الأصلية | الخطة المحدثة
# ---------------------------------------------------------------
with table_area:
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
