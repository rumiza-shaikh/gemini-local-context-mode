# PRD — Local Context Mode (Mini)

## Problem & Users
Global answers feel US-first; EM users bounce when facts (currency, regs, examples) don’t fit.

## Goals
- Inline adaptation of **facts**, not just words
- Measurable lift in **CTR**; reduce **bounce**

## Non-Goals
- Legal advice, full legal workflows
- Heavy per-country retraining

## UX
- Toggle “Make it local”; autolocalize after first use
- Tiny disclaimers + official links; freshness badge
- Copy summary one-click

## Metrics
- **Primary:** CTR
- **Secondary:** scroll depth, pogo-stick rate, copy clicks
- Guardrail events: staleness/forbidden claims

## Experiment / Rollout
- IN/BR/JP only; 50/50 ON/OFF for 14 days
- Ship/Iterate/Kill gates per `EXPERIMENT.md`

## Risks & Mitigations
- Stale facts → watchers + SLA; badge + rollback
- Latency → prefetch/caching; small pack sizes
- Mis-scoped tone → linter + reviews per pack

## Tech / Owners
- **Flow:** Intent → Country Pack → Rewrite → Guardrails → Eval
- **Owners:** PM, Eng, T&S, Legal/Privacy, i18n
