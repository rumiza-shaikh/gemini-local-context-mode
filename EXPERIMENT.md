# A/B Experiment Plan — Local Context Mode

## Objective
Quantify whether inline, market-native facts improve engagement vs. global answers.

## Hypothesis
Local facts (currency, payments, examples, summary compliance cues) **increase CTR** and **reduce bounce**.

## Design
- **Flag:** `local_context_mode` (ON/OFF)
- **Split:** 50/50 by geo buckets within IN/BR/JP
- **Duration:** 14 days (cover day-of-week effects)
- **Surfaces:** Search/Help answer component

## Metrics
- **Primary:** CTR on result interactions (expand/click/copy)
- **Secondary:** Scroll depth, pogo-stick rate, copy clicks

## Power (ballpark)
- Baseline CTR 20%, MDE +5% rel (→ 21%)
- α=0.05, power=0.8 ⇒ ~15–20k exposures/arm (rule-of-thumb)
- If low traffic: extend to 21–28 days or accept larger MDE

## Novelty & Bias Controls
- Pre-register decision rule; primary read on days 3–14
- Exclude bots/admin/test users

## Decision Rule
- **Ship**: CTR ↑ ≥ **+5% rel** and bounce ↓ (p<0.05), no safety regressions
- **Iterate**: CTR flat but scroll ↑ ≥ 3% or bounce ↓ ≥ 3%
- **Rollback**: CTR ↓ or guardrail breaches (>1% flagged sessions)

## Instrumentation
Emit: `variant, market, intent, ctr_click, scroll_depth, bounce, toggle_used, country_selected, copy_clicked`

## Risks & Mitigations
- **Stale/wrong compliance** → summary-only copy, freshness flags, official links
- **Latency** → prefetch small country packs; client cache 24h
