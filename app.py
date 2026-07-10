# -*- coding: utf-8 -*-
"""
منصة الثروة الخاصة — Private Banking Wealth Terminal (v20)
  HEDGING VALUE (قيمة التحوط) — executive display adjustment
  * A numeric input "قيمة التحوط (KD)" (default 0.0) sits inside the
    May Milestones console. The FOCAL May card displays:
        Display_Value = May_Projected_Balance
                        − (Monthly_Spending_Limit − Hedging_Value)
    The delta badge and the top narrative recalculate from this adjusted
    value against the original baseline. The 3-column table remains RAW —
    this adjustment gauges net spending-buffer power in the summary only.
  * The hedging value is fully integrated into the persistence engine
    (cloud gist / localStorage) — it never resets on reload.
  DYNAMIC ACCOUNTING ENGINE — the obligations deduction fires at the
  LAUNCH ROW of each scenario, wherever that row sits in the grid:
  * الخطة الأصلية  launch row (شهر البداية):
        (الرصيد الافتتاحي − total_obligations) + الراتب − حد الصرف
        then: (previous + الراتب) − حد الصرف
  * الخطة المحدثة  launch row (الشهر الحالي — ANY position):
        (الرصيد الفعلي الحالي − total_obligations) + الراتب − حد الصرف
        then: (previous + الراتب) − حد الصرف — a perfect functional
        clone of the baseline launch math; rows before the anchor = '—'
  * total_obligations is summed dynamically from the 4 numeric inputs.
  * The anchor is an ABSOLUTE calendar month (year, month) — changing
    شهر البداية can never shift or alter the updated plan.
  CLOUD SYNC (cross-device persistence)
  * All primary inputs are saved to a PRIVATE GitHub Gist (configured via
    Streamlit Secrets: GH_TOKEN + GIST_ID). Mac, iPhone Safari, and the
    home-screen app all read/write the SAME data — identical numbers on
    every device, and nothing is lost when iOS clears browser storage.
  * If the secrets are not configured, the app automatically falls back
    to device-local storage (streamlit-js-eval / localStorage).
  iOS ICON — dual-path enforcement
  * apple-touch-icon + standalone meta tags are injected BOTH as direct
    HTML markup at the very top of the page AND programmatically into the
    parent <head> (with cache-busting).
  UI
  * Passcode gate "2806", clean sans-serif typography, centered numbers,
    controls → future May milestones → 3-column table → bottom expanders,
    single-screen iPhone fit.
Arabic RTL.
"""

import json

import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_js_eval import streamlit_js_eval
    HAS_STORAGE = True
except Exception:
    HAS_STORAGE = False   # local fallback unavailable; cloud sync may still work

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
# Cache-busted so Safari re-fetches the icon after repo updates
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
# CSS — clean system typography, compressed zero-scroll spacing,
# self-contained blocks. Native widgets stay with config.toml theme.
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

    /* ---------------- Status line ---------------- */
    .status-card {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 9px 14px;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.65;
    }
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

    /* ---------------- May Milestones console ---------------- */
    .may-terminal-title {
        text-align: center; font-size: 0.64rem; font-weight: 700;
        color: #94a3b8; letter-spacing: 3px; margin-bottom: 2px;
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
    .may-k { font-size: 0.6rem; color: #94a3b8; font-weight: 600; margin-bottom: 1px; }
    .may-v {
        font-size: 1.16rem; font-weight: 800; color: #0f172a;
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

    /* ---------------- Data table ---------------- */
    .tbl-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        max-height: 250px;
        overflow-y: auto;
    }
    table.wtable {
        width: 100%; border-collapse: collapse; font-size: 0.76rem;
        font-variant-numeric: tabular-nums;
    }
    table.wtable th {
        position: sticky; top: 0; z-index: 1;
        background: #f8f9fa;
        color: #94a3b8;
        font-size: 0.64rem; font-weight: 700; letter-spacing: 0.5px;
        padding: 8px 6px 6px 6px;
        text-align: center;
        border-bottom: 1px solid #e2e8f0;
    }
    table.wtable td {
        padding: 5px 6px;
        text-align: center;
        color: #0f172a;
        border-bottom: 1px solid #f1f5f9;
    }
    table.wtable td.num { direction: ltr; font-weight: 600; }
    table.wtable td.mut { color: #cbd5e1; font-weight: 400; }
    table.wtable td.neg { color: #b91c1c; font-weight: 700; }

    /* May rows — champagne gold, bold */
    table.wtable tr.may-row td {
        background: rgba(212, 180, 96, 0.14);
        font-weight: 700;
        border-top: 1px solid rgba(212, 180, 96, 0.45);
        border-bottom: 1px solid rgba(212, 180, 96, 0.45);
    }

    /* Anchor row — soft blue, declared last so it wins over May */
    table.wtable tr.anchor-row td {
        background: rgba(37, 99, 235, 0.08);
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
# CLOUD SYNC BACKEND — private GitHub Gist shared by ALL devices.
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
#   hero → anchor inputs → status → May console → table → settings
# ===============================================================
st.markdown('<div class="hero">🏦 منصة الثروة الخاصة</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">PRIVATE WEALTH TERMINAL</div>', unsafe_allow_html=True)

anchor_area = st.container()
status_area = st.container()
terminal_area = st.container()
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

# Dynamic sum of the 4 numeric inputs — never hardcoded
total_obligations = float(sum(obligation_amounts))

# ---------------------------------------------------------------
# Timeline — each month is an ABSOLUTE (year, month) identity
# ---------------------------------------------------------------
timeline, month_labels, month_nums = [], [], []
for i in range(24):
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
            "أيًا كان موقع شهرك في الجدول — وتُحفظ مدخلاتك متزامنة عبر جميع أجهزتك."
        )

anchor_idx = timeline.index(anchor_month_abs)
has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية (baseline)
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(24):
    if i == 0:
        prev = (prev - total_obligations) + float(salary) - float(spend_limit)
    else:
        prev = (prev + float(salary)) - float(spend_limit)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — الخطة المحدثة (dynamic launch-row engine)
# ---------------------------------------------------------------
updated_balances = [None] * 24
if has_anchor:
    prev = (float(anchor_balance) - total_obligations) + float(salary) - float(spend_limit)
    updated_balances[anchor_idx] = prev
    for i in range(anchor_idx + 1, 24):
        prev = (prev + float(salary)) - float(spend_limit)
        updated_balances[i] = prev

# ---------------------------------------------------------------
# May milestones — FUTURE ONLY (at/after the selected current month)
# ---------------------------------------------------------------
all_may_ids = [i for i in range(24) if month_nums[i] == MAY]
future_may_ids = [i for i in all_may_ids if i >= anchor_idx]
target_idx = future_may_ids[0] if future_may_ids else all_may_ids[-1]
target_label = month_labels[target_idx]

# ---------------------------------------------------------------
# May console frame + HEDGING input (قيمة التحوط)
# The frame, title and input are created FIRST so the hedging value
# feeds the executive display math and the status narrative; the
# milestone cards are appended into the same frame further below.
# ---------------------------------------------------------------
with terminal_area:
    may_console = st.container(border=True)
    with may_console:
        st.markdown(
            '<div class="may-terminal-title">منصة أهداف مايو — MAY MILESTONES</div>',
            unsafe_allow_html=True,
        )
        _h1, _h2, _h3 = st.columns([1, 1.3, 1])
        with _h2:
            hedging_value = st.number_input(
                "قيمة التحوط (KD)",
                value=0.0,
                step=50.0,
                key="hedging_value",
            )


# Executive display adjustment for the FOCAL May card ONLY:
#   Display_Value = Projected − (Spending Limit − Hedging Value)
# The 3-column table below stays RAW (core engine law untouched).
raw_target_upd = updated_balances[target_idx]
adjusted_target_upd = (
    raw_target_upd - (float(spend_limit) - float(hedging_value))
    if raw_target_upd is not None else None
)

# ---------------------------------------------------------------
# Status line
# ---------------------------------------------------------------
with status_area:
    if not has_anchor or adjusted_target_upd is None:
        dot, text = "dot-info", (
            "أدخل شهرك الحالي ورصيدك الفعلي لبدء التتبع — تُخصم الالتزامات في "
            "صف الانطلاق ثم يستمر المسار حتى محطة مايو (مع مراعاة قيمة التحوط)."
        )
    else:
        m_std = standard_balances[target_idx]
        m_upd = adjusted_target_upd   # hedging-adjusted executive value
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
# [MIDDLE] May Milestones cards — appended into the console frame.
# FOCAL card shows the hedging-adjusted executive value:
#   Display_Value = Projected − (Spending Limit − Hedging Value)
# All other cards — and the 3-column table below — stay RAW.
# ---------------------------------------------------------------
with may_console:
    if not future_may_ids:
        inner = '<div class="may-empty">لا توجد محطات مايو متبقية في نافذة الخطة الحالية.</div>'
    else:
        cells = ""
        for mi in future_may_ids:
            std_v = standard_balances[mi]
            raw_v = updated_balances[mi]
            is_focal = (mi == target_idx)
            upd_v = adjusted_target_upd if is_focal else raw_v
            sub_note = ('<div class="may-k">بعد هامش التحوط</div>'
                        if (is_focal and upd_v is not None) else "")
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
                {sub_note}
              </div>
              {chip}
            </div>"""
        cols = len(future_may_ids)
        inner = f'<div class="may-grid" style="grid-template-columns: repeat({cols}, 1fr);">{cells}</div>'

    st.markdown(inner, unsafe_allow_html=True)

# ---------------------------------------------------------------
# [BELOW] 3-column table: التاريخ | الخطة الأصلية | الخطة المحدثة
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

if CLOUD_ON:
    # Save only when something actually changed (one API call per edit)
    if st.session_state.get("_last_saved_payload") != _payload:
        if cloud_save(_payload):
            st.session_state["_last_saved_payload"] = _payload
            st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
        else:
            st.caption("⚠️ تعذّر الحفظ السحابي مؤقتًا — سيُعاد تلقائيًا مع أول تعديل قادم")
    else:
        st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
elif HAS_STORAGE:
    _payload_js = json.dumps(json.dumps(_payload, ensure_ascii=False))
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('{STORAGE_KEY}', {_payload_js})",
        key="_ls_write",
    )
    st.caption("💾 حفظ محلي على هذا الجهاز فقط — لتفعيل المزامنة بين الأجهزة أضف GH_TOKEN وGIST_ID في الإعدادات السرية")import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_js_eval import streamlit_js_eval
    HAS_STORAGE = True
except Exception:
    HAS_STORAGE = False   # local fallback unavailable; cloud sync may still work

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
# Cache-busted so Safari re-fetches the icon after repo updates
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
# CSS — clean system typography, compressed zero-scroll spacing,
# self-contained blocks. Native widgets stay with config.toml theme.
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

    /* ---------------- Status line ---------------- */
    .status-card {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 9px 14px;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.65;
    }
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

    /* ---------------- May Milestones console ---------------- */
    .may-terminal {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 12px 10px 12px;
    }
    .may-terminal-title {
        text-align: center; font-size: 0.64rem; font-weight: 700;
        color: #94a3b8; letter-spacing: 3px; margin-bottom: 8px;
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
    .may-k { font-size: 0.6rem; color: #94a3b8; font-weight: 600; margin-bottom: 1px; }
    .may-v {
        font-size: 1.16rem; font-weight: 800; color: #0f172a;
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

    /* ---------------- Data table ---------------- */
    .tbl-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        max-height: 250px;
        overflow-y: auto;
    }
    table.wtable {
        width: 100%; border-collapse: collapse; font-size: 0.76rem;
        font-variant-numeric: tabular-nums;
    }
    table.wtable th {
        position: sticky; top: 0; z-index: 1;
        background: #f8f9fa;
        color: #94a3b8;
        font-size: 0.64rem; font-weight: 700; letter-spacing: 0.5px;
        padding: 8px 6px 6px 6px;
        text-align: center;
        border-bottom: 1px solid #e2e8f0;
    }
    table.wtable td {
        padding: 5px 6px;
        text-align: center;
        color: #0f172a;
        border-bottom: 1px solid #f1f5f9;
    }
    table.wtable td.num { direction: ltr; font-weight: 600; }
    table.wtable td.mut { color: #cbd5e1; font-weight: 400; }
    table.wtable td.neg { color: #b91c1c; font-weight: 700; }

    /* May rows — champagne gold, bold */
    table.wtable tr.may-row td {
        background: rgba(212, 180, 96, 0.14);
        font-weight: 700;
        border-top: 1px solid rgba(212, 180, 96, 0.45);
        border-bottom: 1px solid rgba(212, 180, 96, 0.45);
    }

    /* Anchor row — soft blue, declared last so it wins over May */
    table.wtable tr.anchor-row td {
        background: rgba(37, 99, 235, 0.08);
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
# CLOUD SYNC BACKEND — private GitHub Gist shared by ALL devices.
# Configure once in Streamlit Cloud → Settings → Secrets:
#   GH_TOKEN = "ghp_xxxxxxxx"   (classic token, 'gist' scope only)
#   GIST_ID  = "xxxxxxxxxxxxxxxx"
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
# Primary: shared cloud gist (identical data on every device).
# Fallback: this device's localStorage (when secrets not configured).
# ===============================================================
PERSISTED_WIDGET_KEYS = (
    ["start_month", "start_year", "init_balance", "currency", "salary", "spend_limit", "anchor_balance"]
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
#   hero → anchor inputs → status → May console → table → settings
# ===============================================================
st.markdown('<div class="hero">🏦 منصة الثروة الخاصة</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">PRIVATE WEALTH TERMINAL</div>', unsafe_allow_html=True)

anchor_area = st.container()
status_area = st.container()
terminal_area = st.container()
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

# Dynamic sum of the 4 numeric inputs — never hardcoded
total_obligations = float(sum(obligation_amounts))

# ---------------------------------------------------------------
# Timeline — each month is an ABSOLUTE (year, month) identity
# ---------------------------------------------------------------
timeline, month_labels, month_nums = [], [], []
for i in range(24):
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
            "أيًا كان موقع شهرك في الجدول — وتُحفظ مدخلاتك متزامنة عبر جميع أجهزتك."
        )

anchor_idx = timeline.index(anchor_month_abs)
has_anchor = anchor_balance is not None

# ---------------------------------------------------------------
# Chain 1 — الخطة الأصلية (baseline)
#   Launch row (شهر البداية):
#       (initial − total_obligations) + salary − spending
#   Row n : (previous + salary) − spending
# ---------------------------------------------------------------
standard_balances = []
prev = float(initial_balance)
for i in range(24):
    if i == 0:
        prev = (prev - total_obligations) + float(salary) - float(spend_limit)
    else:
        prev = (prev + float(salary)) - float(spend_limit)
    standard_balances.append(prev)

# ---------------------------------------------------------------
# Chain 2 — الخطة المحدثة (dynamic launch-row engine)
#   Fully independent loop — reads NOTHING from the baseline chain.
#   * rows BEFORE the anchor : None → rendered as '—'
#   * the anchor LAUNCH row (wherever الشهر الحالي sits in the grid):
#       (الرصيد الفعلي الحالي − total_obligations) + salary − spending
#       — the obligations deduction fires HERE, at the dynamic starting
#         point of the projection, a perfect clone of the baseline's
#         launch math. It does NOT depend on the row being first.
#   * all FUTURE rows        : (previous + salary) − spending
# ---------------------------------------------------------------
updated_balances = [None] * 24
if has_anchor:
    prev = (float(anchor_balance) - total_obligations) + float(salary) - float(spend_limit)
    updated_balances[anchor_idx] = prev
    for i in range(anchor_idx + 1, 24):
        prev = (prev + float(salary)) - float(spend_limit)
        updated_balances[i] = prev

# ---------------------------------------------------------------
# May milestones — FUTURE ONLY (at/after the selected current month)
# ---------------------------------------------------------------
all_may_ids = [i for i in range(24) if month_nums[i] == MAY]
future_may_ids = [i for i in all_may_ids if i >= anchor_idx]
target_idx = future_may_ids[0] if future_may_ids else all_may_ids[-1]
target_label = month_labels[target_idx]

# ---------------------------------------------------------------
# Status line
# ---------------------------------------------------------------
with status_area:
    if not has_anchor or updated_balances[target_idx] is None:
        dot, text = "dot-info", (
            "أدخل شهرك الحالي ورصيدك الفعلي لبدء التتبع — تُخصم الالتزامات في "
            "صف الانطلاق نفسه ثم يستمر المسار (+ الراتب − حد الصرف) حتى محطة مايو."
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
# [MIDDLE] May Milestones console — future milestones only
# ---------------------------------------------------------------
with terminal_area:
    if not future_may_ids:
        inner = '<div class="may-empty">لا توجد محطات مايو متبقية في نافذة الخطة الحالية.</div>'
    else:
        cells = ""
        for mi in future_may_ids:
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
        cols = len(future_may_ids)
        inner = f'<div class="may-grid" style="grid-template-columns: repeat({cols}, 1fr);">{cells}</div>'

    st.markdown(
        f"""
        <div class="may-terminal">
          <div class="may-terminal-title">منصة أهداف مايو — MAY MILESTONES</div>
          {inner}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# [BELOW] 3-column table: التاريخ | الخطة الأصلية | الخطة المحدثة
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

# ===============================================================
# PERSISTENCE — SAVE (runs after all inputs are known)
# Primary: PATCH the shared gist whenever any input changes.
# Fallback: mirror into this device's localStorage.
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
}
for i in range(1, 5):
    _payload[f"ob_name_{i}"] = st.session_state.get(f"ob_name_{i}", "")
    _payload[f"ob_amount_{i}"] = float(st.session_state.get(f"ob_amount_{i}", 0.0))

if CLOUD_ON:
    # Save only when something actually changed (one API call per edit)
    if st.session_state.get("_last_saved_payload") != _payload:
        if cloud_save(_payload):
            st.session_state["_last_saved_payload"] = _payload
            st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
        else:
            st.caption("⚠️ تعذّر الحفظ السحابي مؤقتًا — سيُعاد تلقائيًا مع أول تعديل قادم")
    else:
        st.caption("☁️ محفوظ ومتزامن عبر جميع أجهزتك")
elif HAS_STORAGE:
    _payload_js = json.dumps(json.dumps(_payload, ensure_ascii=False))
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('{STORAGE_KEY}', {_payload_js})",
        key="_ls_write",
    )
    st.caption("💾 حفظ محلي على هذا الجهاز فقط — لتفعيل المزامنة بين الأجهزة أضف GH_TOKEN وGIST_ID في الإعدادات السرية")
