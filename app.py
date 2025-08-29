import os, time, json, csv
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

# ---------------- Config & Paths ----------------
st.set_page_config(page_title='Local Context Intelligence — Prototype', layout='wide')

ROOT = Path(__file__).parent
DATA_PATH = ROOT / 'data' / 'localized_content.json'
MOCK_METRICS_CSV = ROOT / 'data' / 'mock_metrics.csv'     # for predicted CTR (mock)
METRICS_LOG = ROOT / 'data' / 'metrics.jsonl'             # observed events (local log)
STYLES_PATH = ROOT / 'styles.css'

# OPTIONAL: Google Form sink for events (set as env vars if you use it)
FORM_URL = os.getenv("FORM_URL", "").strip()              # e.g., https://docs.google.com/forms/.../formResponse
FORM_FIELDS = {  # replace with your Form entry IDs if you use a Google Form
    "kind": os.getenv("FORM_KIND", "entry.1111111111"),
    "country": os.getenv("FORM_COUNTRY", "entry.2222222222"),
    "extra": os.getenv("FORM_EXTRA", "entry.3333333333"),
    "ts": os.getenv("FORM_TS", "entry.4444444444"),
}

# ---------------- Styles ----------------
if STYLES_PATH.exists():
    st.markdown(f'<style>{STYLES_PATH.read_text()}</style>', unsafe_allow_html=True)

# ---------------- Utilities: Telemetry ----------------
def _append_local_event(ev: dict):
    """Append an event line to metrics.jsonl (best-effort)."""
    try:
        METRICS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(METRICS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev) + "\n")
    except Exception:
        pass

def _post_form(ev: dict):
    """Optionally POST to Google Form if configured (best-effort, non-blocking)."""
    if not FORM_URL:
        return
    try:
        import requests  # lazy import
        payload = {
            FORM_FIELDS["kind"]: ev.get("kind", ""),
            FORM_FIELDS["country"]: ev.get("country", ""),
            FORM_FIELDS["extra"]: ev.get("extra", ""),
            FORM_FIELDS["ts"]: str(int(ev.get("ts", time.time()))),
        }
        requests.post(FORM_URL, data=payload, timeout=2)
    except Exception:
        pass

def log_event(kind: str, country: str = "", extra: str = ""):
    ev = {"kind": kind, "country": country, "extra": extra, "ts": time.time()}
    _append_local_event(ev)
    _post_form(ev)

def load_observed_metrics():
    """Aggregate metrics.jsonl into simple KPIs for the ribbon."""
    events = []
    if METRICS_LOG.exists():
        with open(METRICS_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    # Sessions heuristic: unique 10-minute buckets × country (demo-level)
    buckets = {(int(e.get("ts", 0)) // 600, e.get("country","")) for e in events}
    sessions = max(len(buckets), 0)

    toggle_used = sum(1 for e in events if e.get("kind") == "toggle_used")
    country_selected = sum(1 for e in events if e.get("kind") == "country_selected")
    copy_clicked = sum(1 for e in events if e.get("kind") == "copy_clicked")
    scroll_gain_vals = [float(e.get("extra", 0) or 0) for e in events if e.get("kind") == "scroll_gain"]

    out = {
        "sessions": sessions,
        "%_toggle_used": round(100 * (toggle_used / sessions), 1) if sessions else 0.0,
        "avg_country_switches": round(country_selected / sessions, 2) if sessions else 0.0,
        "copy_clicks": copy_clicked,
        "observed_scroll_gain": round(sum(scroll_gain_vals) / max(len(scroll_gain_vals), 1), 2) if scroll_gain_vals else 0.0,
        "N": sessions
    }
    return out

def freshness_badge(updated_at_iso: str | None):
    """Render 'Updated <date> • Freshness checked X day(s) ago'."""
    try:
        if not updated_at_iso:
            raise ValueError("no date")
        dt = datetime.fromisoformat(updated_at_iso.replace("Z","+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
        st.caption(f"🕒 Updated {dt.date().isoformat()} • Freshness checked {days} day(s) ago")
    except Exception:
        st.caption("🕒 Updated date unavailable")

def render_disclaimers(block: dict):
    """Render summary-only disclaimers with official links (if present)."""
    refs = block.get("regulatory_refs") or block.get("sources") or []
    if refs:
        with st.expander("Context & sources"):
            st.write("_Summary only; not legal advice._")
            for r in refs:
                name = r.get("name") or r.get("title") or "Source"
                desc = r.get("disclaimer") or r.get("note") or ""
                url = r.get("url") or r.get("link") or ""
                if url:
                    st.markdown(f"- **{name}** — {desc} • [Official link]({url})")
                else:
                    st.markdown(f"- **{name}** — {desc}")

# ---------------- Header ----------------
st.markdown('# Gemini Local Context Mode')
st.markdown('Toggle Gemini Search into **local context mode** to instantly adapt examples, metrics, and regulations — **no extra prompts**.')

with st.expander("❓ Isn't this just Google Translate?", expanded=False):
    st.markdown(
        """
**No.**  
A **language translator** converts the *same* meaning from Language A → Language B.  
- Example: “How to start a bakery” → “Cómo abrir una panadería” (same facts, different language).  
- Goal: **Fidelity to original text**.

**Local Context Mode** rewrites the answer so it’s *trusted, actionable, and relevant* **for a specific market**.  
- It **changes the facts**, not just the words:
  - **India** → FSSAI license, INR costs, Swiggy/Zomato  
  - **Brazil** → CNPJ, BRL costs, ANVISA  
  - **Japan** → 保健所許可, 円 (JPY), LINE marketing  
- Goal: **Fidelity to intent + full localization** (regulations, currency, examples, tone).

**One-liner:** *Translate changes the words. Local Context Mode changes the world around those words so the answer feels like it was written for you.*
        """
    )

# ---------------- Load Data ----------------
if DATA_PATH.exists():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
else:
    data = {'queries': {}}

entries = data.get('queries', {})

# ---------------- Controls ----------------
colA, colB = st.columns([3, 1])
with colA:
    query = st.text_input('Search', value='How to start a small bakery', placeholder='Type a query…')
with colB:
    # Local mode toggle
    if "local_mode" not in st.session_state:
        st.session_state.local_mode = True
    local_mode = st.toggle('Local Context Mode', value=st.session_state.local_mode, help='When ON, results adapt to selected market automatically.')
    # Log toggle change
    if local_mode != st.session_state.local_mode:
        st.session_state.local_mode = local_mode
        # We'll log after we know the country selection (below)

countries = ['India 🇮🇳', 'Brazil 🇧🇷', 'Japan 🇯🇵']

if hasattr(st, "segmented_control"):
    country = st.segmented_control('Market', options=countries, selection_mode='single', default=countries[0])
else:
    country = st.radio('Market', options=countries, index=0, horizontal=True)

country_key = country.split()[0]  # "India" from "India 🇮🇳"
normalized_q = (query or "").strip().lower()

# Track & log selection changes
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country_key
if country_key != st.session_state.prev_country:
    log_event("country_selected", country_key)
    st.session_state.prev_country = country_key

if "prev_local_mode" not in st.session_state:
    st.session_state.prev_local_mode = local_mode
if local_mode != st.session_state.prev_local_mode:
    log_event("toggle_used", country_key, str(local_mode))
    st.session_state.prev_local_mode = local_mode

# ---------------- KPI Ribbon ----------------
# Load mocked country CTR predictions (if present)
ctr_map = {}
if MOCK_METRICS_CSV.exists():
    with open(MOCK_METRICS_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ctr_map[row['country']] = row

# Observed vs Mocked toggle
obs = load_observed_metrics()
mock_mode = st.toggle("Show mocked metrics", value=False, help="Use only if you lack traffic. Toggles the panel below.")

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

st.write('')
k1, k2, k3, k4 = st.columns(4)
if mock_mode:
    country_pred = ctr_map.get(country_key, {'predicted_ctr_lift_pct': '—'})
    kpi_box(k1, 'Predicted CTR lift', f"+{country_pred.get('predicted_ctr_lift_pct','—')}%", 'Mocked: vs baseline English')
    kpi_box(k2, 'Extra scroll depth', '+6.5%', 'Mocked: localized relevance increases dwell time')
    kpi_box(k3, 'Bounce rate change', '−9.2%', 'Mocked: compliance clarity reduces pogo-sticking')
    kpi_box(k4, 'Copy clicks', '14', 'Mocked: demo interaction proxy')
    st.caption('Mocked metrics • Replace with your experiment readout when available.')
else:
    kpi_box(k1, 'Sessions (N)', f"{obs['sessions']}", '10-min bucket heuristic')
    kpi_box(k2, '% used Local mode', f"{obs['%_toggle_used']}%", 'Observed')
    kpi_box(k3, 'Avg country switches', f"{obs['avg_country_switches']}", 'Observed')
    kpi_box(k4, 'Copy clicks', f"{obs['copy_clicks']}", 'Observed')
    st.caption(f"Observed (N={obs['N']}) • Scroll gain: +{obs['observed_scroll_gain']}% (small N)")

st.write('')

# ---------------- Results ----------------
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
    block = entry.get(country_key if local_mode else 'Global', entry.get('Global', {}))

    # Mode pill
    flag = country.split()[-1] if ' ' in country else ''
    pill_class = 'pill on' if local_mode else 'pill'
    mode_label = 'Local Context' if local_mode else 'Global Default'
    pill_html = (
        f'<div class="{pill_class}">'
        f'<span class="flag">{flag}</span>'
        f'<strong>{mode_label}</strong>'
        '</div>'
    )
    st.markdown(pill_html, unsafe_allow_html=True)

    # Result card
    st.write('')
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f"### {block.get('title','')}", unsafe_allow_html=True)

    # Freshness badge (tries block.updated_at → entry.updated_at → data.updated_at)
    updated_iso = block.get("updated_at") or entry.get("updated_at") or data.get("updated_at")
    freshness_badge(updated_iso)

    # Summary bullets
    for bullet in block.get('summary', []):
        st.markdown(f"- {bullet}")

    # Currency/notes
    if 'currency_note' in block:
        st.markdown(f"<div class='small'>{block['currency_note']}</div>", unsafe_allow_html=True)

    # Callouts
    callouts = block.get('callouts', [])
    if callouts:
        st.markdown('<div class="callouts">', unsafe_allow_html=True)
        for c in callouts:
            st.markdown(f"<span class='badge'>{c}</span> ", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Copy area (+ log)
    localized_bullets = block.get('summary', [])
    if localized_bullets:
        st.write('')
        text_to_copy = "\n".join(f"• {b}" for b in localized_bullets)
        st.text_area("Copy localized summary", text_to_copy, height=140)
        if st.button("Copy to clipboard"):
            log_event("copy_clicked", country_key)
            st.success("Copied! (logged)")

    # Disclaimers & sources (tiny, expandable)
    render_disclaimers(block)

    # Footer line: report issue
    st.markdown(
        "🔎 [Report an issue](https://github.com/<you>/<repo>/issues/new) • "
        "Links go to official sources where possible."
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Feedback ----------------
st.markdown(
    "💬 **Have 30 seconds?** "
    "[Give quick feedback](https://docs.google.com/forms/d/e/1FAIpQLSe_M7GyFxxvy6xmJu7tZxkqBMmwJ9tgHYL7VmEsLjBF-FBUHQ/viewform) — clarity, usefulness, and what’s missing.",
    help="Helps prioritize what to add next."
)

# ---------------- Experiment & About ----------------
with st.expander('Experiment plan (A/B)'):
    st.markdown(
        """
**Hypothesis:** Inline market-native facts increase CTR and reduce bounce vs. global answers.  
**Design:** 50/50 ON vs OFF by geo buckets (IN/BR/JP), **14 days**.  
**Primary:** CTR on result interactions. **Secondary:** scroll depth, pogo-sticking, copy clicks.  
**Power:** Detect +5% relative CTR at 80% power; extend duration if traffic is low.  
**Decision rule:**  
- **Ship** if CTR ↑ ≥ **+5% rel** and bounce ↓ (p<0.05) with no safety regressions.  
- **Iterate** if CTR flat but scroll ↑ ≥ 3% or bounce ↓ ≥ 3%.  
- **Rollback** on regressions or guardrail breaches (>1% flagged sessions).
        """
    )

with st.expander('About this prototype'):
    st.markdown(
        '- **Purpose:** Demonstrate an inline, zero-prompt localization toggle for Gemini Search.\n'
        '- **Markets:** India, Brazil, Japan (contrast in language, regulation, currency).\n'
        '- **Data:** Demo JSON with simplified regulatory notes — not legal advice.\n'
        '- **Metrics:** Observed panel (events.jsonl) or mocked (toggle above).'
    )

# Optional: log a small scroll gain once per run (demo)
# log_event("scroll_gain", country_key, "6.0")
