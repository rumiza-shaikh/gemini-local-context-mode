# Persona & Journey — Local Context Intelligence (LCI)

## 1) Persona Overview
- **Name, Location:** Riya — Mumbai, India  
- **Background:** Aspiring small business owner  
- **Goal:** Start a neighborhood bakery within 60 days  
- **Pain Points today:** US-centric answers; USD costs; unclear permits; low trust; pogo-sticking

---

## 2) Journey Map (Before vs After LCI)

| Step / Moment | User thought | **Without LCI** (today) | **With LCI** (LCI ON) | Metric & Target | Instrumentation |
|---|---|---|---|---|---|
| 1. Search “how to start a bakery” | “What are the steps for Mumbai?” | US fees/permits; USD; generic advice | **₹** costs; **FSSAI/GST** named; **Context & sources** expander | **CTR +5% rel** on answer actions | `ctr_click` |
| 2. Skim requirements | “Do I need a license?” | Vague “health permit” | **FSSAI levels** (Basic/State/Central) + **official link**; **Summary only** copy | **Bounce −3%** | `scroll_depth`, `pogo` |
| 3. Check costs & units | “Can I afford this?” | USD; inches | **₹ ranges**; **mm** units; UPI POS cue | **Time on answer +3%** | `scroll_depth` |
| 4. Trust check | “Is this current?” | No freshness signal | **Updated <date>**; freshness status; linkouts | **User flags <1%** | `report_issue`, `error_flag_rate` |
| 5. Next action | “Save steps” | Copy/paste from multiple tabs | **Copy summary** button; clear bullets | **Copy clicks +10%** (observed) | `copy_clicked` |

**Edge/Failure states:**  
- **Stale pack:** Show staleness badge + fallback to Global summary with sources.  
- **Unsupported locale:** Keep Global, invite feedback.  
- **Sensitive query:** Do not localize; show safe global with official links.

---

## 3) Moments of Delight & Friction
- **Delight:** “Finally ₹/FSSAI/GST in one place—with a source.”  
- **Friction:** Wants **Hindi** toggle; long regulator names truncate on mobile.

**Accessibility notes:** WCAG 2.2 AA contrast; screen-reader labels (“Local Context, on/off”); keyboard focus visible.

---

## 4) Callout Quotes
> “With LCI, I finally found info that actually applies to me.”  
> “I trusted it because it cited Indian government sources.”

---

## 5) Summary Box
- **Before LCI:** Frustration; multiple tabs; low trust; bounce.  
- **After LCI:** Fast, **local facts** inline; **Updated** date + sources; confident next step.

---

## 6) Acceptance Criteria (v0)
- **Impact:** CTR **+5% rel**, Bounce **−3%**, Scroll **+3%** (p<.05) in IN pilot  
- **Quality:** P0 factual errors ≤ **0.5% / 10k** impressions; auto-rollback > **1%/h**  
- **Perf:** Added latency ≤ **80ms P50 / 150ms P95**  
- **Safety:** Summary-only compliance; ≥1 official link present when regulators are named


[Watch the video](data/Riya_Mumbai.mp4)
