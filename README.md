# Local Context Intelligence (LCI) — Search Prototype

> **Changes facts, not just words.**  
> Inline, market-native answers for India, Brazil, and Japan — with currency, regulators, units, sources, and freshness.

<p align="center">
  <img src="assets/demo.gif" width="900" alt="LCI demo: Global → India → Brazil → Japan" />
</p>

---

### Quick links
**Live demo:** <https://gemini-local-context-mode.streamlit.app> •
**90s video:** <https://tinyurl.com/2h54knxe> •
**PRD:** [/docs/PRD.md](docs/PRD.md) •
**Experiment plan:** [/docs/Experiment_Plan.md](docs/Experiment_Plan.md) •
**Events:** [/docs/Events_Dictionary.yaml](docs/Events_Dictionary.yaml)

---

## TL;DR
A thin-slice Search enhancement that localizes **facts** — not just language — for **IN/BR/JP**. Visible **Updated** dates and **official sources**, fast enough for Search, shipped behind a **14-day flag** with **auto-rollback**. Guardrails for hallucinations, safety exclusions, and regional QA are built in.

---

## Why this matters (and why now)
- Users outside the US often get **US-first** answers (USD, US regs, inches). Trust drops; pogo-sticking increases.  
- **Gemini-class guided rewrites** now make structured, locale-aware changes feasible at scale.  
- Growth + regulatory scrutiny demand **transparent, local, safe** answers with sources.

---

## Not a translator (explicitly)
**Translation** keeps the *same* facts in a different language.  
**LCI** rewrites the *facts* for a locale: currency, regulators, units, examples, tone.

> **Example (query: “How to start a small bakery”)**  
> **IN** → ₹ ranges, **FSSAI** levels, **GST** thresholds, UPI cue  
> **BR** → R$ ranges, **CNPJ**, **ANVISA/Vigilância Sanitária**, Pix cue  
> **JP** → ¥ ranges, **mm** units, **保健所** permit, インボイス mention

---

## What’s in the prototype
- **Inline LCI control**: Global ↔ Local (remembers per session)  
- **Local facts**: currency/units, regulators/permits, local trust cues (UPI/Pix), representative examples  
- **Trust**: “**Summary only**” phrasing, **Updated \<date\>**, **Context & sources** (≥1 official link)  
- **Safety**: freshness SLA & staleness badge, sensitive-topic exclusions, fallback to global safe summary  
- **Markets**: India 🇮🇳, Brazil 🇧🇷, Japan 🇯🇵 (one flagship intent: *start_bakery*)

---

## Screens & metrics (mock)
<p align="center">
  <img src="assets/LCI_Dashboard_Mock.png" width="900" alt="LCI A/B dashboard mock: CTR, Bounce, Scroll, Quality & Performance SLOs, rollout state." />
</p>

**Week 2 (A/B Day 6, mock):**  
CTR **21.4%** vs 20.0% control (**+7.0% rel, p=0.021**) • Bounce **11.9%** vs 12.5% (**−4.8% rel**) • Scroll **56.1%** vs 54.0% (**+3.9% rel**) • Toggle usage **68%** of LCI sessions • Latency add **P50 +38 ms / P95 +112 ms** (PASS) • Staleness **0.8%** (PASS) • Error flags **0.2%/h** (PASS) • N≈**85k**/arm

> Real runs would follow the plan in `Experiment_Plan.md` with ship/iterate/rollback thresholds.



Responsible AI & safety

Sources required: every compliance cue cites ≥1 official, whitelisted link.

Hallucination SLI with auto-rollback if >1%/h.

Summary-only tone (no procedural/legal guarantees).

Sensitive topics are not localized; show safe global with official links.

Human-in-the-loop: regional review, monthly fairness audit.

