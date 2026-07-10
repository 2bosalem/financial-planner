# -*- coding: utf-8 -*-
"""
منصة الثروة الخاصة — Private Banking Wealth Terminal (v26)
  DESIGN PASS — professional visibility upgrade:
  * Variance box removed from the May card (per design decision); the
    tinted status banner carries the Target-vs-Projected comparison.
  * State-tinted status banner (green/amber/red/blue), hero result pill
    in the hedging cradle, larger high-contrast metrics, zebra table
    with stronger header band and deeper row highlights.
  THE ISOLATED HEDGING CRADLE (صندوق التحوط المستقل)
  * One input "قيمة التحوط (KD)" + one readout "الرصيد المستهدف الحالي":
        Target_Result = Current Real Cash − (Spending Limit − Hedging)
    Box-only value — never injected into any array, loop, or table cell.
  UPCOMING MAY MILESTONE CARD — located by DATE-LABEL search; shows the
  baseline and the RAW projected balance extracted from the table row.
  Beyond the 18-month window: '—' + "بانتظار التحديث".
  PERSISTENCE — every input (incl. قيمة التحوط and the 4 obligations)
  mirrors to browser localStorage on change and auto-restores on boot
  (streamlit-js-eval — required in requirements.txt). Optional gist sync.
  ENGINE — 18-month horizon, launch-row obligations deduction, absolute
  (year, month) anchoring; the table shows pure recursive balances only.
  iOS — passcode "2806", apple-touch-icon + standalone tags, system
  typography, strict center alignment, single-viewport packing.
Arabic RTL. All values in KD.
"""

import json

import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_js_eval import streamlit_js_eval
    HAS_STORAGE = True
except Exception:
    HAS_STORAGE = False   # local bridge unavailable; cloud sync may still work

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
STORAGE_KEY = "wealth_terminal_v1"
HORIZON = 18     # exactly 18 continuous chronological months
APPLE_ICON_URL = "https://raw.githubusercontent.com/2bosalem/financial-planner/main/icon.png?v=2"

# ---------------------------------------------------------------
# iOS icon path 1 — direct HTML markup at the very top of the page.
# ---------------------------------------------------------------
st.markdown(
    f"""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="منصة الثروة">
    <link rel="apple-touch-icon" sizes="180x180" href="{APPLE_ICON_URL}">
    <link rel="apple-touch-icon" href="{APPLE_ICON_URL}">
    <link rel="apple-touch-icon-precomposed" href="{APPLE_ICON_URL}">
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# iOS icon path 2 — programmatic injection into the parent <head>
# ---------------------------------------------------------------
components.html(
    f"""
    <script>
    (function() {{
        const doc = window.parent.document;
        doc.querySelectorAll(
            'link[rel="apple-touch-icon"], link[rel="apple-touch-icon-precomposed"]'
        ).forEach(el => el.remove());
        const rels = ['apple-touch-icon', 'apple-touch-icon-precomposed'];
        for (const rel of rels) {{
            const link = doc.createElement('link');
            link.rel = rel;
            link.sizes = '180x180';
            link.href = '{APPLE_ICON_URL}';
            doc.head.appendChild(link);
        }}
        const metas = [
            ['apple-mobile-web-app-capable', 'yes'],
            ['mobile-web-app-capable', 'yes'],
            ['apple-mobile-web-app-status-bar-style', 'default'],
            ['apple-mobile-web-app-title', 'منصة الثروة'],
        ];
        for (const [name, content] of metas) {{
            if (doc.head.querySelector(`meta[name="${{name}}"]`)) continue;
            const m = doc.createElement('meta');
            m.name = name;
            m.content = content;
            doc.head.appendChild(m);
        }}
    }})();
    </script>
    """,
    height=0,
)

# ---------------------------------------------------------------
# CSS — professional visibility pass: high-contrast typography,
# tinted status states, hero pill, zebra table.
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Clean system typography — icon-font safe */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
    .stApp input, .stApp button, .stApp td, .stApp th {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     system-ui, "Helvetica Neue", Arial, sans-serif;
    }
    [data-testid="stIconMaterial"],
    span[class*="material-symbols"],
    i[class*="material-icons"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* Phone-frame canvas, compressed for a single iPhone viewport */
    .stApp { direction: rtl; }
    .block-container {
        max-width: 540px;
        padding-top: 0.7rem;
        padding-bottom: 0.4rem;
    }
    [data-testid="stVerticalBlock"] { gap: 0.5rem; }
    [data-testid="stHorizontalBlock"] { gap: 0.6rem; }
    header[data-testid="stHeader"] { height: 1.2rem; background: transparent; }
    /* Collapse the zero-height component iframes so they leave no gap */
    [data-testid="stElementContainer"]:has(iframe[height="0"]) { display: none; }

    /* Widgets: spacing + centered values only */
    label[data-testid="stWidgetLabel"] p { font-size: 0.74rem; font-weight: 600; }
    [data-testid="stNumberInput"] input { direction: ltr; text-align: center; font-weight: 600; }
    [data-testid="stTextInput"] input { text-align: center; font-weight: 600; }
    [data-testid="stExpander"] summary p { font-size: 0.78rem; font-weight: 600; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
    [data-testid="stCaptionContainer"] p { font-size: 0.66rem; margin: 0; text-align: center; }
    .stButton button, .stFormSubmitButton button { border-radius: 12px; font-weight: 700; }

    /* ---------------- Hero ---------------- */
    .hero {
        text-align: center; font-size: 1.08rem; font-weight: 700;
        color: #0f172a; letter-spacing: 0.3px; margin: 0;
    }
    .hero-sub {
        text-align: center; font-size: 0.64rem; font-weight: 600;
        color: #94a3b8; letter-spacing: 2.5px; margin: 0 0 2px 0;
    }

    /* ---------------- Secure gate ---------------- */
    .gate-icon { text-align: center; font-size: 2.4rem; margin: 2.2rem 0 0.4rem 0; }
    .gate-title { text-align: center; font-size: 1.02rem; font-weight: 700; color: #0f172a; margin: 0; }
    .gate-sub { text-align: center; font-size: 0.72rem; color: #94a3b8; margin: 2px 0 10px 0; }

    /* ---------------- Status line (state-tinted) ---------------- */
    .status-card {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 9px 14px;
        text-align: center;
        font-size: 0.82rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.65;
    }
    .status-card.st-green { background: #ecfdf5; border-color: #a7f3d0; }
    .status-card.st-amber { background: #fffbeb; border-color: #fde68a; }
    .status-card.st-red   { background: #fef2f2; border-color: #fecaca; }
    .status-card.st-info  { background: #eff6ff; border-color: #bfdbfe; }

    /* Hedging cradle result pill — the hero number of the dashboard */
    .hedge-pill {
        display: inline-block; direction: ltr;
        font-size: 1.5rem; font-weight: 800;
        font-variant-numeric: tabular-nums;
        padding: 4px 26px; border-radius: 14px;
        background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857;
    }
    .hedge-pill.neg { background: #fef2f2; border-color: #fecaca; color: #b91c1c; }
    .hedge-pill.mut { background: #f1f5f9; border-color: #e2e8f0; color: #94a3b8; }
    .status-dot {
        display: inline-block; width: 8px; height: 8px;
        border-radius: 50%; margin-left: 7px; vertical-align: 1px;
    }
    .dot-green { background: #059669; }
    .dot-amber { background: #d97706; }
    .dot-red   { background: #b91c1c; }
    .dot-info  { background: #2563eb; }
    .status-strong { font-weight: 800; }
    .t-green { color: #047857; }
    .t-amber { color: #b45309; }
    .t-red   { color: #b91c1c; }

    /* ---------------- Consoles / cards ---------------- */
    .may-terminal-title {
        text-align: center; font-size: 0.72rem; font-weight: 800;
        color: #64748b; letter-spacing: 3px; margin-bottom: 8px;
    }
    .may-grid { display: grid; gap: 10px; }
    .may-cell {
        text-align: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 10px 8px 9px 8px;
    }
    .may-year {
        font-size: 0.82rem; font-weight: 800; color: #0f172a;
        margin-bottom: 7px; letter-spacing: 0.3px;
    }
    .may-item { margin-bottom: 6px; }
    .may-k { font-size: 0.68rem; color: #64748b; font-weight: 700; margin-bottom: 2px; }
    .may-v {
        font-size: 1.35rem; font-weight: 800; color: #0b1220;
        direction: ltr; text-align: center; line-height: 1.2;
        font-variant-numeric: tabular-nums;
    }
    .may-v.pos { color: #047857; }
    .may-v.neg { color: #b91c1c; }
    .may-v.mut { color: #cbd5e1; font-weight: 400; }
    .delta-chip {
        display: inline-block; direction: ltr;
        font-size: 0.66rem; font-weight: 700; color: #ffffff;
        padding: 2px 12px; border-radius: 999px;
    }
    .stApp .chip-pos, .stApp .chip-neg { color: #ffffff; }
    .chip-pos { background: #047857; }
    .chip-neg { background: #b91c1c; }
    .chip-mut { background: #eef1f5; color: #94a3b8; }
    .may-empty {
        text-align: center; font-size: 0.74rem; color: #94a3b8; padding: 6px 0;
    }

    /* ---------------- Data table (visibility upgrade) ---------------- */
    .tbl-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        max-height: 250px;
        overflow-y: auto;
    }
    table.wtable {
        width: 100%; border-collapse: collapse; font-size: 0.8rem;
        font-variant-numeric: tabular-nums;
    }
    table.wtable th {
        position: sticky; top: 0; z-index: 1;
        background: #eef2f7;
        color: #475569;
        font-size: 0.68rem; font-weight: 800; letter-spacing: 0.5px;
        padding: 9px 6px 7px 6px;
        text-align: center;
        border-bottom: 2px solid #dbe2ec;
    }
    table.wtable td {
        padding: 7px 6px;
        text-align: center;
        color: #0b1220;
        border-bottom: 1px solid #eef1f6;
    }
    table.wtable tr:nth-child(even) td { background: #f8fafc; }
    table.wtable td.num { direction: ltr; font-weight: 600; }
    table.wtable td.mut { color: #cbd5e1; font-weight: 400; }
    table.wtable td.neg { color: #b91c1c; font-weight: 700; }

    /* May rows — champagne gold, bold */
    table.wtable tr.may-row td {
        background: rgba(212, 180, 96, 0.22);
        font-weight: 700;
        border-top: 1px solid rgba(212, 180, 96, 0.45);
        border-bottom: 1px solid rgba(212, 180, 96, 0.45);
    }

    /* Anchor row — soft blue, declared last so it wins over May */
    table.wtable tr.anchor-row td {
        background: rgba(37, 99, 235, 0.12);
        font-weight: 700;
        border-top: 1.5px solid #2563eb;
        border-bottom: 1.5px solid #2563eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt(x: float) -> str:
    """Thousands-separated number, no decimals."""
    return f"{x:,.0f}"


# ===============================================================
# OPTIONAL CLOUD SYNC — private GitHub Gist shared by ALL devices.
# ===============================================================
GIST_FILE = "wealth_data.json"


def _cloud_configured() -> bool:
    try:
        return bool(st.secrets["GH_TOKEN"]) and bool(st.secrets["GIST_ID"])
    except Exception:
        return False


CLOUD_ON = _cloud_configured()


def _gh_headers() -> dict:
    return {
        "Authorization": f"token {st.secrets['GH_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def cloud_load() -> dict | None:
    """Fetch the shared JSON blob from the private gist (one call/session)."""
    try:
        r = requests.get(
            f"https://api.github.com/gists/{st.secrets['GIST_ID']}",
            headers=_gh_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            content = r.json().get("files", {}).get(GIST_FILE, {}).get("content", "")
            if content.strip():
                return json.loads(content)
    except Exception:
        pass
    return None


def cloud_save(payload: dict) -> bool:
    """Write the shared JSON blob back to the private gist."""
    try:
        r = requests.patch(
            f"https://api.github.com/gists/{st.secrets['GIST_ID']}",
            headers=_gh_headers(),
            json={"files": {GIST_FILE: {"content": json.dumps(payload, ensure_ascii=False, indent=1)}}},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


# ===============================================================
# SECURE GATE
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
# PERSISTENCE — LOAD (runs before any widget is created)
# ===============================================================
PERSISTED_WIDGET_KEYS = (
    ["start_month", "start_year", "init_balance", "currency", "salary", "spend_limit",
     "anchor_balance", "hedging_value"]
    + [f"ob_name_{i}" for i in range(1, 5)]
    + [f"ob_amount_{i}" for i in range(1, 5)]
)


def _apply_saved(saved: dict) -> None:
    for _k in PERSISTED_WIDGET_KEYS:
        if _k in saved:
            st.session_state[_k] = saved[_k]
    if isinstance(saved.get("anchor_abs_month"), list):
        st.session_state["anchor_abs_month"] = tuple(saved["anchor_abs_month"])


if not st.session_state.get("_storage_loaded", False):
    if CLOUD_ON:
        _saved = cloud_load()
        if _saved:
            try:
                _apply_saved(_saved)
            except Exception:
                pass
        st.session_state["_storage_loaded"] = True
    elif HAS_STORAGE:
        _raw = streamlit_js_eval(
            js_expressions=f"localStorage.getItem('{STORAGE_KEY}')",
            key="_ls_read",
        )
        if _raw:
            try:
                _apply_saved(json.loads(_raw))
            except Exception:
                pass
            st.session_state["_storage_loaded"] = True

# ===============================================================
# MAIN TERMINAL — strict top-to-bottom sequence:
#   hero → anchor inputs → status → hedging cradle → May card →
#   table → settings
# ===============================================================
st.markdown('<div class="hero">🏦 منصة الثروة الخاصة</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">PRIVATE WEALTH TERMINAL</div>', unsafe_allow_html=True)

anchor_area = st.container()
status_area = st.container()
hedge_area = st.container()        # standalone hedging cradle
terminal_area = st.container()     # upcoming May milestone card
table_area = st.container()
settings_area = st.container()

# ---------------------------------------------------------------
# Settings (bottom of page visually, executed first for values)
# ---------------------------------------------------------------
with settings_area:
    with st.expander("الإعدادات الأساسية", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            start_month = st.selectbox(
                "شهر البداية",
                options=list(range(1, 13)),
                format_func=lambda m: MONTH_NAMES[m - 1],
                index=7,  # أغسطس
                key="start_month",
            )
            initial_balance = st.number_input("الرصيد الافتتاحي", value=80410.0, step=500.0, key="init_balance")
            currency = st.text_input("العملة", value="KD", max_chars=8, key="currency")
        with c2:
            start_year = st.number_input("سنة البداية", min_value=2020, max_value=2100, value=2026, step=1, key="start_year")
            salary = st.number_input("الراتب الشهري", min_value=0.0, value=3300.0, step=100.0, key="salary")
            spend_limit = st.number_input("حد الصرف الشهري", min_value=0.0, value=5000.0, step=100.0, key="spend_limit")

    with st.expander("الالتزامات السنوية الأربعة — تُخصم عند صف الانطلاق في كل خطة", expanded=False):
        default_obligations = [
            ("الالتزام السنوي 1", 7300.0),
            ("الالتزام السنوي 2", 7300.0),
            ("الالتزام السنوي 3", 7300.0),
            ("الالتزام السنوي 4", 7300.0),
        ]
        obligation_amounts = []
        for i, (d_name, d_amount) in enumerate(default_obligations, start=1):
            n_col, a_col = st.columns([1.4, 1])
            n_col.text_input(f"الالتزام {i}", value=d_name, key=f"ob_name_{i}")
            obligation_amounts.append(
                a_col.number_input(f"المبلغ {i}", min_value=0.0, value=d_amount, step=100.0, key=f"ob_amount_{i}")
            )

# Dynamic liability aggregation — never hardcoded
total_obligations = float(sum(obligation_amounts))

# ---------------------------------------------------------------
# Timeline — 18 months; each month is an ABSOLUTE (year, month) identity
# ---------------------------------------------------------------
timeline, month_labels, month_nums = [], [], []
for i in range(HORIZON):
    m = (start_month - 1 + i) % 12
    y = int(start_year) + (start_month - 1 + i) // 12
    timeline.append((y, m))
    month_labels.append(f"{MONTH_NAMES[m]} {y}")
    month_nums.append(m)

# Restored/previous anchor may fall outside a re-based window — reset safely
if st.session_state.get("anchor_abs_month") not in timeline:
    st.session_state["anchor_abs_month"] = timeline[0]

# ---------------------------------------------------------------
# [TOP] Current Status Update — anchor inputs (absolute month anchor)
# ---------------------------------------------------------------
with anchor_area:
    with st.container(border=True):
        a1, a2 = st.columns(2)
        with a1:
            anchor_month_abs = st.selectbox(
                "الشهر الحالي",
                options=timeline,
                format_func=lambda t: f"{MONTH_NAMES[t[1]]} {t[0]}",
                index=0,
                key="anchor_abs_month",
            )
        with a2:
            anchor_balance = st.number_input(
                "الرصيد الفعلي الحالي",
                value=None,
                step=100.0,
                placeholder="أدخل رصيدك…",
                key="anchor_balance",
            )
        st.caption(
            f"صف الانطلاق يُحسب: (رصيدك − الالتزامات {fmt(total_obligations)}) + الراتب − حد الصرف "
            "أيًا كان موقع شهرك في الجدول — وتُحفظ مدخلاتك تلقائيًا."
        )

anchor_idx = timeline.index(anchor_month_abs)
has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية (baseline, 18 rows)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(HORIZON):
    if i == 0:
        prev = (prev - total_obligations) + float(salary) - float(spend_limit)
    else:
        prev = (prev + float(salary)) - float(spend_limit)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — الخطة المحدثة (dynamic launch-row engine, same cutoff)
# ---------------------------------------------------------------
updated_balances = [None] * HORIZON
if has_anchor:
    prev = (float(anchor_balance) - total_obligations) + float(salary) - float(spend_limit)
    updated_balances[anchor_idx] = prev
    for i in range(anchor_idx + 1, HORIZON):
        prev = (prev + float(salary)) - float(spend_limit)
        updated_balances[i] = prev

# ---------------------------------------------------------------
# Upcoming May milestone — located by DATE-LABEL search (never by
# positional index). A past May can never be selected.
# ---------------------------------------------------------------
_ay, _am = anchor_month_abs                      # (year, 0-based month)
first_may_year = _ay if _am <= MAY else _ay + 1
upcoming_label = f"مايو {first_may_year}"
may_idx = month_labels.index(upcoming_label) if upcoming_label in month_labels else None
target_label = upcoming_label

# ---------------------------------------------------------------
# THE ISOLATED HEDGING CRADLE (صندوق التحوط المستقل)
#   Target_Result = Current Real Cash − (Spending Limit − Hedging)
# Box-only value — never injected into any array, loop, or table cell.
# ---------------------------------------------------------------
with hedge_area:
    with st.container(border=True):
        st.markdown(
            '<div class="may-terminal-title">صندوق التحوط — HEDGING CRADLE</div>',
            unsafe_allow_html=True,
        )
        _c1, _c2, _c3 = st.columns([1, 1.3, 1])
        with _c2:
            hedging_value = st.number_input(
                "قيمة التحوط (KD)",
                value=0.0,
                step=50.0,
                key="hedging_value",
            )
        target_result = (
            float(anchor_balance) - (float(spend_limit) - float(hedging_value))
            if has_anchor else None
        )
        if target_result is None:
            _pill = '<span class="hedge-pill mut">—</span>'
        else:
            _pill_cls = "neg" if target_result < 0 else ""
            _pill = f'<span class="hedge-pill {_pill_cls}">{fmt(target_result)} {currency}</span>'
        st.markdown(
            '<div style="text-align:center;">'
            '<div class="may-k">الرصيد المستهدف الحالي</div>'
            f'{_pill}</div>',
            unsafe_allow_html=True,
        )

# Raw projected balance for the upcoming May — extracted directly from
# that month's row in the lower data table (pure, unadjusted).
raw_may = updated_balances[may_idx] if may_idx is not None else None
may_variance = (target_result - raw_may
                if (target_result is not None and raw_may is not None) else None)

# ---------------------------------------------------------------
# Status line — narrative driven by the May variance (state-tinted)
# ---------------------------------------------------------------
with status_area:
    if may_variance is None:
        dot, text = "dot-info", (
            "أدخل شهرك الحالي ورصيدك الفعلي لبدء التتبع — سيُحسب رصيدك المستهدف "
            f"في صندوق التحوط ويُقارن بتوقع {target_label} تلقائيًا."
        )
    else:
        _ref = max(abs(raw_may), 1.0)
        if may_variance >= 0:
            dot = "dot-green"
            text = (
                f'استقرار إيجابي — رصيدك المستهدف <span class="status-strong">{fmt(target_result)} {currency}</span> '
                f'يتقدم على توقع {target_label} ({fmt(raw_may)}) بفارق '
                f'<span class="status-strong t-green">+{fmt(may_variance)}</span>.'
            )
        elif abs(may_variance) <= 0.10 * _ref:
            dot = "dot-amber"
            text = (
                f'انحراف بسيط — رصيدك المستهدف {fmt(target_result)} {currency} أدنى من توقع '
                f'{target_label} ({fmt(raw_may)}) بمقدار '
                f'<span class="status-strong t-amber">−{fmt(abs(may_variance))}</span>. قابل للتصحيح.'
            )
        else:
            dot = "dot-red"
            text = (
                f'عجز واضح — رصيدك المستهدف {fmt(target_result)} {currency} أدنى من توقع '
                f'{target_label} ({fmt(raw_may)}) بمقدار '
                f'<span class="status-strong t-red">−{fmt(abs(may_variance))}</span>. قلّل الصرف اليومي.'
            )
    _tint = dot.replace("dot-", "st-")
    st.markdown(
        f'<div class="status-card {_tint}"><span class="status-dot {dot}"></span>{text}</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# [MIDDLE] Upcoming May milestone card — two clean metric cells.
# ---------------------------------------------------------------
with terminal_area:
    with st.container(border=True):
        st.markdown(
            f'<div class="may-terminal-title">المحطة القادمة — {target_label}</div>',
            unsafe_allow_html=True,
        )
        if may_idx is None:
            card_html = ('<div class="may-empty">—<br>بانتظار التحديث '
                         '(خارج نافذة الـ 18 شهرًا)</div>')
        else:
            std_v = standard_balances[may_idx]
            std_cls = "neg" if std_v < 0 else ""
            raw_html = ('<div class="may-v mut">—</div>' if raw_may is None
                        else f'<div class="may-v {"neg" if raw_may < 0 else ""}">{fmt(raw_may)}</div>')
            # Two clean metric cells only — the variance box was removed by
            # design decision; the top status banner carries the comparison.
            card_html = (
                '<div class="may-grid" style="grid-template-columns: 1fr 1fr;">'
                '<div class="may-cell">'
                '<div class="may-k">الخطة الأصلية</div>'
                f'<div class="may-v {std_cls}">{fmt(std_v)}</div>'
                '</div>'
                '<div class="may-cell">'
                '<div class="may-k">الخطة المحدثة (خام من الجدول)</div>'
                f'{raw_html}'
                '</div>'
                '</div>'
            )
        st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------------
# [BELOW] 3-column table — RAW recursive balances only (18 rows).
# ---------------------------------------------------------------
with table_area:
    rows = ""
    for i in range(HORIZON):
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

# ===============================================================
# PERSISTENCE — SAVE (runs after all inputs are known)
# ===============================================================
_payload = {
    "start_month": int(start_month),
    "start_year": int(start_year),
    "init_balance": float(initial_balance),
    "currency": currency,
    "salary": float(salary),
    "spend_limit": float(spend_limit),
    "anchor_abs_month": list(anchor_month_abs),
    "anchor_balance": float(anchor_balance) if has_anchor else None,
    "hedging_value": float(hedging_value),
}
for i in range(1, 5):
    _payload[f"ob_name_{i}"] = st.session_state.get(f"ob_name_{i}", "")
    _payload[f"ob_amount_{i}"] = float(st.session_state.get(f"ob_amount_{i}", 0.0))

# LocalStorage mirror — ALWAYS active: every input survives page
# close/refresh on this device regardless of cloud configuration.
if HAS_STORAGE:
    _payload_js = json.dumps(json.dumps(_payload, ensure_ascii=False))
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('{STORAGE_KEY}', {_payload_js})",
        key="_ls_write",
    )

# Optional cloud layer on top (cross-device sync via private gist)
if CLOUD_ON:
    # Save only when something actually changed (one API call per edit)
    if st.session_state.get("_last_saved_payload") != _payload:
        if cloud_save(_payload):
            st.session_state["_last_saved_payload"] = _payload
            st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
        else:
            st.caption("⚠️ تعذّر الحفظ السحابي مؤقتًا — محفوظ محليًا وسيُعاد تلقائيًا")
    else:
        st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
elif HAS_STORAGE:
    st.caption("💾 محفوظ تلقائيًا على هذا الجهاز — أرقامك تعود كما هي عند كل فتح")
