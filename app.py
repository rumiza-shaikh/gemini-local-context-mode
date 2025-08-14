import json, csv
import streamlit as st
from pathlib import Path

st.set_page_config(page_title='Gemini Local Context Mode — Prototype', layout='wide')

DATA_PATH = Path(__file__).parent / 'data' / 'localized_content.json'
METRICS_PATH = Path(__file__).parent / 'data' / 'mock_metrics.csv'
STYLES_PATH = Path(__file__).parent / 'styles.css'

# Load styles (optional)
if STYLES_PATH.exists():
    st.markdown(f'<style>{STYLES_PATH.read_text()}</style>', unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown('# Gemini Local Context Mode')
st.markdown('Toggle Gemini Search into **local context mode** to instantly adapt examples, metrics, and regulations — **no extra prompts**.')

# 🔍 Make the translator vs localization difference explicit
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

**One‑liner:** *Translate changes the words. Local Context Mode changes the world around those words so the answer feels like it was written for you.*
        """
    )

# ---------------- Data ----------------
if DATA_PATH.exists():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
else:
    # graceful fallback so the app still renders
    data = {'queries': {}}

# ---------------- Controls ----------------
colA, colB = st.columns([3, 1])
with colA:
    query = st.text_input('Search', value='How to start a small bakery', placeholder='Type a query…')
with colB:
    local_mode = st.toggle('Local Context Mode', value=True, help='When ON, results adapt to selected market automatically.')

countries = ['India 🇮🇳', 'Brazil 🇧🇷', 'Japan 🇯🇵']

# Use segmented control if available; otherwise, fallback to radio
if hasattr(st, "segmented_control"):
    country = st.segmented_control('Market', options=countries, selection_mode='single', default=countries[0])
else:
    country = st.radio('Market', options=countries, index=0, horizontal=True)

country_key = country.split()[0]  # "India" from "India 🇮🇳"
normalized_q = (query or "").strip().lower()

# ---------------- KPIs ----------------
ctr_map = {}
if METRICS_PATH.exists():
    with open(METRICS_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ctr_map[row['country']] = row

st.write('')
k1, k2, k3 = st.columns(3)

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

ctr = ctr_map.get(country_key, {'predicted_ctr_lift_pct': '—', 'notes': ''})
kpi_box(k1, 'Predicted CTR lift', f"+{ctr.get('predicted_ctr_lift_pct','—')}%", 'Mocked: vs baseline English')
kpi_box(k2, 'Extra scroll depth', '+6.5%', 'Mocked: localized relevance increases dwell time')
kpi_box(k3, 'Bounce rate change', '−9.2%', 'Mocked: compliance clarity reduces pogo-sticking')

st.write('')

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
        '- **Purpose:** Demonstrate an inline, zero‑prompt localization toggle for Gemini Search.\n'
        '- **Markets:** India, Brazil, Japan (contrast in language, regulation, currency).\n'
        '- **Data:** Demo JSON with simplified regulatory notes — not legal advice.\n'
        '- **Metrics:** Mocked to show where product KPIs would surface.'
    )
