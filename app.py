import json, csv, time
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

# ---------------- Paths ----------------
ROOT = Path(__file__).parent
DATA_PATH = ROOT / 'data' / 'localized_content.json'
METRICS_PATH = ROOT / 'data' / 'mock_metrics.csv'
LOG_PATH = ROOT / 'data' / 'metrics.jsonl'
STYLES_PATH = ROOT / 'styles.css'

# ---------------- Page & Styles ----------------
st.set_page_config(page_title='Local Context Intelligence — Prototype', layout='wide')

if STYLES_PATH.exists():
    st.markdown(f"<style>{STYLES_PATH.read_text()}</style>", unsafe_allow_html=True)

# ---------------- Small helpers ----------------
def now_ts() -> int:
    return int(time.time())

def log_event(kind: str, country: str = "", extra: str = ""):
    """Append lightweight telemetry to data/metrics.jsonl"""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": now_ts(), "kind": kind, "country": country, "extra": extra}
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def parse_iso(dt: str):
    try:
        # Allow both '...Z' and offset-less strings
        if dt.endswith("Z"):
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return datetime.fromisoformat(dt)
    except Exception:
        return None

def days_since(dt: str) -> str:
    d = parse_iso(dt)
    if not d:
        return "—"
    delta = datetime.now(timezone.utc) - d.astimezone(timezone.utc)
    return str(max(0, delta.days))

def kpi_box(col, title, value, sub=''):
    with col:
        html = (
            '<div class="kpi">'
            f'<div style="font-size:14px;color:#334155">{title}</div>'
            f'<div style="font-size:28px;font-weight:600">{value}</div>'
            f'<div class="small">{sub}</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

# ---------------- Session state ----------------
st.session_state.setdefault("toggle_used", 0)
st.session_state.setdefault("country_switches", 0)
st.session_state.setdefault("copy_clicks", 0)
st.session_state.setdefault("prev_country", None)
st.session_state.setdefault("prev_local_mode", None)

# ---------------- Header ----------------
st.markdown('# Local Context Intelligence')
st.markdown(
    'Turn on the **Local Context Mode** to instantly adapt examples, metrics, currency, and regulations — '
    '**no extra prompts**.'
)

# 🔍 Make the translator vs localization difference explicit
with st.expander("❓ Why not just Language Translation?", expanded=False):
    st.markdown(
        """  
A **language translator** converts the *same* meaning from Language A → Language B.  
- Example: “How to start a bakery” → “Cómo abrir una panadería” (same facts, different language).  
- Goal: **Fidelity to original text**.

**Local Context Intelligence (LCI)** rewrites the answer so it’s *trusted, actionable, and relevant* **for a specific market**.  
- It **changes the facts**, not just the words:
  - **India** → FSSAI license, GST thresholds, ₹ costs, UPI cues  
  - **Brazil** → CNPJ, ANVISA/Vigilância Sanitária, R$ costs, Pix  
  - **Japan** → 保健所許可, ¥, **mm** units
- Goal: **Fidelity to intent + full localization** (regulations, currency, examples, tone).

**One-liner:** *Translate changes the words. LCI changes the world around those words so the answer feels like it was written for you.*
        """
    )

# ---------------- Load Data ----------------
if DATA_PATH.exists():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
else:
    data = {'queries': {}}

ctr_map = {}
if METRICS_PATH.exists():
    with METRICS_PATH.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ctr_map[row['country']] = row

# ---------------- Controls ----------------
colA, colB = st.columns([3, 1])
with colA:
    query = st.text_input('Search', value='How to start a small bakery', placeholder='Type a query…')
with colB:
    local_mode = st.toggle('Local Context Mode', value=True, help='When ON, results adapt to selected market automatically.')

countries = ['India 🇮🇳', 'Brazil 🇧🇷', 'Japan 🇯🇵']

if hasattr(st, "segmented_control"):
    country = st.segmented_control('Market', options=countries, selection_mode='single', default=countries[0])
else:
    country = st.radio('Market', options=countries, index=0, horizontal=True)

country_key = country.split()[0]  # "India" from "India 🇮🇳"
normalized_q = (query or "").strip().lower()

# Telemetry on control changes
if st.session_state["prev_country"] is None:
    st.session_state["prev_country"] = country_key
elif st.session_state["prev_country"] != country_key:
    st.session_state["country_switches"] += 1
    st.session_state["prev_country"] = country_key
    log_event("country_selected", country_key)

if st.session_state["prev_local_mode"] is None:
    st.session_state["prev_local_mode"] = local_mode
elif st.session_state["prev_local_mode"] != local_mode:
    st.session_state["prev_local_mode"] = local_mode
    st.session_state["toggle_used"] += 1
    log_event("toggle_used", country_key, extra=str(local_mode))

# ---------------- KPI strip ----------------
st.write('')
k1, k2, k3 = st.columns(3)

ctr = ctr_map.get(country_key, {'predicted_ctr_lift_pct': '—', 'notes': ''})
kpi_box(k1, 'Predicted CTR lift', f"+{ctr.get('predicted_ctr_lift_pct','—')}%", 'Mocked: vs baseline English')
kpi_box(k2, 'Extra scroll depth', '+6.5%', 'Mocked: localized relevance increases dwell time')
kpi_box(k3, 'Bounce rate change', '−9.2%', 'Mocked: clarity reduces pogo-sticking')

# Observed (this session)
st.caption(
    f"**Observed (this session):** toggle_used={st.session_state['toggle_used']} • "
    f"country_switches={st.session_state['country_switches']} • copy_clicks={st.session_state['copy_clicks']}"
)

# ---------------- Results ----------------
entries = data.get('queries', {})
entry = entries.get(normalized_q)

if entry is None:
    st.info(
        'Demo content available for 3 sample queries:\n'
        '• How to start a small bakery\n'
        '• How to open a student savings account\n'
        '• How to register an e-commerce business'
    )
else:
    # Choose localized vs global block
    raw_block = entry.get(country_key if local_mode else 'Global', entry.get('Global', {}))
    # Some entries include nested variants; flatten if needed
    block = raw_block
    if isinstance(raw_block, dict) and "variants" in raw_block:
        block = raw_block["variants"].get("en", next(iter(raw_block["variants"].values())))

    # Mode pill
    flag = country.split()[-1] if ' ' in country else ''
    pill_class = 'pill on' if local_mode else 'pill'
    mode_label = 'LCI On' if local_mode else 'Global'
    pill_html = (
        f'<div class="{pill_class}">'
        f'<span class="flag">{flag}</span>'
        f'<strong>{mode_label}</strong>'
        '</div>'
    )
    st.markdown(pill_html, unsafe_allow_html=True)

    # Updated date / freshness
    updated_at = block.get("updated_at") or entry.get("updated_at")
    freshness = days_since(updated_at) if updated_at else "—"
    updated_label = f"Updated {updated_at[:10]}" if updated_at else "Updated —"

    # Result card
    st.write('')
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### {block.get('title','')}", unsafe_allow_html=True)

    for bullet in block.get('summary', []):
        st.markdown(f"- {bullet}")

    if 'currency_note' in block:
        st.markdown(f"<div class='small'>{block['currency_note']}</div>", unsafe_allow_html=True)

    callouts = block.get('callouts', [])
    if callouts:
        st.markdown('<div class="callouts">', unsafe_allow_html=True)
        for c in callouts:
            st.markdown(f"<span class='badge'>{c}</span> ", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Context & sources
    st.markdown('<hr style="border:none;border-top:1px solid #eee;margin:12px 0 8px 0">', unsafe_allow_html=True)
    with st.expander("Context & sources"):
        st.markdown(
            f"- **Freshness:** {updated_label} • Freshness checked {freshness} day(s) ago"
        )
        refs = block.get('regulatory_refs', [])
        if refs:
            st.markdown("**Official links** (summary-only; verify requirements):")
            for r in refs:
                name = r.get("name", "Source")
                url = r.get("url", "")
                disc = r.get("disclaimer", "")
                st.markdown(f"- [{name}]({url}) — {disc}")

    # Copy summary (counts clicks; browser clipboard not guaranteed)
    summary_text = "\n".join(block.get("summary", []))
    cols_copy = st.columns([1, 4])
    with cols_copy[0]:
        if st.button("Copy summary"):
            st.session_state["copy_clicks"] += 1
            log_event("copy_clicked", country_key)
            st.success("Copied (or ready to copy).")
    with cols_copy[1]:
        st.caption("Tip: Use this to paste into notes or share with a teammate.")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    "💬 **Have 30 seconds?** "
    "[Give quick feedback](https://docs.google.com/forms/d/e/1FAIpQLSe_M7GyFxxvy6xmJu7tZxkqBMmwJ9tgHYL7VmEsLjBF-FBUHQ/viewform) — clarity, usefulness, and what’s missing.",
    help="Helps prioritize what to add next."
)

# ---------------- Footer ----------------
st.write('')
with st.expander('About this prototype'):
    st.markdown(
        '- **Purpose:** Demonstrate an inline, zero-prompt localization toggle for Search/Help surfaces.\n'
        '- **Markets:** India, Brazil, Japan (contrast in language, regulation, currency).\n'
        '- **Data:** Demo JSON with simplified regulatory notes — **summary only, not legal advice**.\n'
        '- **Metrics:** Mocked KPI cards + observed session counters (see top).'
    )
