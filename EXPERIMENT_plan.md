# Experimentation Plan — Local Context Intelligence (LCI)

_Last updated: 2025-09-02_

---

## A. Objective
Prove that **Local Context Intelligence (LCI)** increases **trusted engagement** on answer modules vs. baseline Search.

---

## B. Hypothesis & Null
- **H1:** LCI increases **CTR on answer interactions** by **≥ +5% relative** and decreases **pogo/bounce** by **≥ −3%** in **IN/BR/JP**.  
- **H0:** No difference between LCI and Control.

---

## C. Variants
- **Control:** Standard answer (**Global** view only).  
- **Treatment:** **LCI** module available; default **OFF**, user can turn **ON** (sticky per session).

---

## D. Eligibility & Exclusions
- **Geo:** IN, BR, JP only.  
- **Intent:** `start_bakery` (flagship) queries and close paraphrases.  
- **Exclusions:** bots/spiders, internal IPs, users with `< 2s` dwell, users on sensitive/legal/medical queries.

---

## E. Randomization & Unit of Analysis
- **Unit:** session (first eligible answer view per session).  
- **Stratification:** by country; **50/50 split** within each geo bucket.  
- **Time boxing:** local **midnight–midnight**; exclude partial days during ramps.

---

## F. Metrics & Definitions

**Primary KPI**  
- **CTR on answer interactions:**  
  `ctr_click_rate = (# of 'ctr_click' events on the answer) / (# of eligible answer views)`

**Secondary**
- **Scroll depth:** average `%` of answer scrolled **(0–100)**.  
- **Pogo/bounce rate:** `%` sessions that click into an answer then **return to SERP within 10s**.  
- **Feature adoption:** `%` LCI sessions with `toggle_used >= 1`.

**Quality & Safety**
- **Staleness rate:** `%` LCI sessions where `updated_at > SLA`.  
- **Error flag rate:** user **Report issue** submissions / LCI sessions.  
- **Hallucination SLI:** suspected factual errors per **10k impressions** (human triage).

**Performance**
- **Latency:** **added** `P50`/`P95` for answer render (ms).

> **Event names:** `ctr_click`, `toggle_used`, `country_selected`, `copy_clicked`, `scroll_depth`, `pogo`, `staleness_flag`, `error_flag`.

---

## G. Statistical Plan
- **Tests:** two-proportion z-test (CTR, pogo); t-test or Mann–Whitney (scroll).  
- **α = 0.05** (two-sided).  
- **Power check:** For baseline CTR ≈ **20%** and **MDE = +5% rel** (to **21%**), need ≈ **90k sessions/arm** (rule-of-thumb; refine with real baselines).  
- **Variance reduction:** **CUPED** or pre-period adjustment if variance is high.

---

## H. Instrumentation Checks (pre-launch)
- Verified logging for: `ctr_click`, `toggle_used`, `country_selected`, `copy_clicked`, `scroll_depth`, `pogo`, `staleness_flag`, `error_flag`.  
- Consistency: events present in **both arms**; **no leakage** across variants.

---

## I. Rollout & Guardrails
- **Shadow mode:** **7 days** (collect candidate outputs; **no user exposure**).  
- **Ramp:** **1% → 5% → 25% → 50%** (per geo), with **24h hold** at each step.  

**Auto-rollback triggers (any):**
- Latency `P95 > 150 ms` for **30 min**  
- Staleness `> 2%` sessions  
- Error flags `> 1%/h`  
- Any **P0** factual issue

---

## J. Decision Rules
- **Ship:** CTR ↑ **≥ +5% rel**, pogo ↓, SLOs met (**p < .05**).  
- **Iterate:** CTR flat **but** scroll ↑ **≥ +3%** **or** pogo ↓ **≥ −3%**.  
- **Rollback:** regression on primary **or** any guardrail breach.

---

## K. Timeline & Owners
- **Week 0:** QA, shadow, power re-calc.  
- **Week 1–2:** A/B live, daily review.  
- **Week 3:** Readout → **ship / iterate / rollback**.  

**Owners:** PM (analysis), Eng (flags/telemetry), SRE (SLOs), Regional leads (quality).

---

# Metrics Dashboard Mock (what to show)

## 1) Overview (top row)
- **CTR (Control vs LCI)** — by country; **bars** with `%` and **+rel lift** callout.  
- **Pogo/Bounce** — **line** over time (daily), green if trending down.  
- **Scroll depth** — average `%` (**stat box**).

## 2) Quality & Safety
- **Staleness rate** — **stat + sparkline**; threshold line at **2%**.  
- **Error flag rate** — **stat**; link to **top issues**.  
- **Hallucination SLI** — `/10k impressions`; **red** if `≥ 1%/h`.

## 3) Performance
- **Latency P50/P95** — **dual stat boxes**; badge **PASS/FAIL** vs SLO.

## 4) Adoption & Usage
- **LCI toggle usage** — `%` sessions where **ON**.  
- **Copy summary clicks** — **count & rate** (proxy for utility).

## 5) Experiment State
- **Rollout status** — **Shadow / 1% / 5% / 25% / 50%** (per geo).  
- **Sample sizes & power** — per arm, per geo; **MDE** bar.

> **Notes panel:** “**Auto-rollback after 1h breach; human-in-the-loop triage before ship.**”  
> *(Mock this in Slides/Figma, or a Google Sheet with bold stat tiles.)*

---

### Optional embed (if you add a mock image)
```html
<p align="center">
  <img src="../assets/LCI_Dashboard_Mock.png" width="900"
       alt="LCI A/B dashboard mock: CTR, Bounce, Scroll, Quality & Performance SLOs, rollout state." />
</p>
