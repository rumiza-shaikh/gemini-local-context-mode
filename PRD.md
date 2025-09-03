Product Requirements Document (PRD)
Local Context Intelligence (LCI) for Google Search




Doc owner: Rumiza Shakeel Shaikh
Last updated: 09/02/2025
Prototype: https://gemini-local-context-mode.streamlit.app/ 
Demo video: https://tinyurl.com/2h54knxe 
Repo: https://github.com/rumiza-shaikh/gemini-local-context-mode
Contact: ss4287@cornell.edu 
LinkedIn: https://www.linkedin.com/in/rumiza-shaikh/



TL;DR
A thin-slice Search enhancement that localizes facts, not just words, inline for India, Brazil, and Japan. Visible sources and freshness, fast enough for Search, shipped behind a 14-day flag with clear decision gates.  Includes built-in hallucination monitoring, rapid rollback, and regional QA for trust and safety.




1) Problem & Why Now
User pain. Many answers read US-first (USD, US regs, US examples). Users in IN/BR/JP lack market-native facts (₹/FSSAI/GST; R$/CNPJ/ANVISA; ¥/mm/保健所), reducing trust and increasing pogo-sticking.
Why now.
Model capability: AI-class guided rewrites are reliable for structured changes.
Business/regulatory pressure: Non-US growth + scrutiny on AI answers → need sources, freshness, safety in-line.
2) Goal & Success Metrics
Goal. Make answers feel local by default while staying fast and safe.
Primary KPI: CTR on answer interactions (target +5% rel vs control).
Secondary: Scroll depth (+3%); Bounce/pogo (−3%); LCI adoption (% sessions using local view).
Performance SLO: added latency ≤ 80 ms P50 / 150 ms P95.
Quality SLO: incorrect/stale compliance cues < 1% of sessions (auto-rollback on breach).
3) Users & JTBD
Riya (IN): needs actionable steps to start a bakery (₹, FSSAI/GST).
Lucas (BR): needs compliance cues (CNPJ/ANVISA) + local trust (Pix).
Yuki (JP): expects ¥, mm, and 保健所 permits.
 JTBD: “When I ask how/what questions, show facts that fit my market so I can act with confidence.”
4) Experience (v0)
Entry. For eligible intents, the answer shows a small Local Context control (remembers choice per session).
When ON (inline rewrite):
Facts: currency/units (₹/R$/¥; mm), regulators/permits (FSSAI/GST; CNPJ/ANVISA; 保健所/インボイス), and local cues (UPI/Pix).
Trust: “Summary only” language, Updated <date>, and Context & sources (≥1 official link).
Fallback: If freshness is stale/unknown, show safe global summary + links.


Flagship intent: “How to start a small bakery” across IN/BR/JP.
 (v0 keeps one intent to isolate impact and risk.)
5) Scope
In v0: IN/BR/JP; one intent (start_bakery); guardrails (summary-only, freshness badge, source link-outs); logging (ctr_click, toggle_used, country_selected, copy_clicked, scroll_depth, pogo).
 Out of v0: legal/medical/financial advice; deep personalization; other domains (banking/housing), path to scale later.
6) Requirements
Functional
Detect eligible intent + locale; expose Local Context control.
On ON, render localized facts in the answer (currency/regs/examples/tone).
Show Updated <date> and Context & sources with at least one official link.
Enforce guardrails (summary-only wording; no procedural guarantees).
Log events (above) with variant ON/OFF.


Non-functional
Latency within SLOs; packs cached 24h.
Freshness SLA (business setup): 14 days → staleness badge.
Accessible copy/labels; readable units/currency (WCAG 2.2 AA).
7) Approach (thin slice)
Pipeline: Intent → Country pack (facts) → Inline rewrite (AI guidance) → Guardrails (summary/freshness/links) → Logging.
 Country pack (v0): country, updated_at, currency, units, regulatory_refs[{name,url,disclaimer}], platform_cues, tone, freshness_sla_days.
 Caching: client-side 24h; background refresh.
 Fallback: guardrail/staleness → global safe summary + links.
 Perf: packs <10 KB; added latency target ≤80 ms P50 / ≤150 ms P95.

8) Experiment & Decision
Design: 14-day feature-flag A/B (geo-bucketed IN/BR/JP; single intent).
 Ship gate: CTR ↑ ≥ +5% rel, Bounce ↓, SLOs met (p<.05).
 Iterate: CTR flat but Scroll ↑ ≥ 3% or Bounce ↓ ≥ 3%.
 Rollback: metric regression or SLO/guardrail breach.
Shadow mode baseline for 7 days pre-launch to ensure no silent regressions.
9) Rollout
Week 0–1: finalize packs; regional QA; verify logging.
Week 2–3: run A/B; daily freshness/safety checks.
Week 4: readout → ship/iterate/rollback; publish pack authoring guide.
Fast-follow: add open student account using same pack.


10) Risks & Mitigations
Risk
Mitigation
Stale/incorrect compliance cues
Updated badge, official links, 24h cache + watchers, quick rollback
Latency regressions
Small packs, client cache, precompute when feasible
“Just translation” perception
Explicit facts change (regs/currency/examples) + visible sources
Sensitive/policy topics
Summary-only copy, exclusions, regional review before launch

11) Responsible AI & User Trust
Hallucination SLIs: ≤ 0.5% suspected factual errors per 10k impressions; auto-rollback if > 1% over 1h.
Source policy: Every localized compliance cue cites ≥1 whitelisted official link; no crowd wikis.
Summary-only guardrail: Never provide procedural/legal guarantees; tone lint enforces hedge words.
User feedback loop: Inline “Was this helpful?” and “Report an issue.” P0 issues disable LCI for that locale.
Human-in-the-loop: Country packs reviewed monthly by regional leads; bias/fairness audit before widening rollout.
All AI-generated facts are visually indicated and always cite at least one official source.
12) Model & Prompt Operations
Prompt/version control: Each answer logs model_version, prompt_id, and pack_version. Changes require PR + reviewer + A/B.
Offline eval set: 200 queries × 3 locales with gold references (currency, regulator names, unit expectations).
Shadow mode: Run LCI OFF for users but log candidate outputs for 7 days to baseline error/latency before exposure.
Prompt A/B: Maintain two guided-rewrite prompts; select by factual accuracy (human eval), then CTR.
13) Monitoring, SLOs & On-call
Dashboards: CTR, scroll, bounce; latency P50/P95, staleness rate, error flag rate, feedback volume.
Auto-rollback triggers: (a) latency P95 >150 ms for 30m, (b) staleness >2% sessions, (c) error flags >1%/h.
Freshness ops: 24h pack cache; watchers ping official sites; weekly freshness review with owners.
On-call: Pager rotation during experiment; runbook for disable/rollback per locale.
14) Privacy & Data Use
Data minimization: Log aggregate events only (ctr_click, toggle_used, etc.); no extra raw query storage beyond standard Search logging.
PII: Country packs hold no PII; telemetry is anonymous/aggregated.
Regional compliance: Data residency follows existing Search policy; cross-region edits require approval.
Retention: 90-day cap on LCI telemetry; user deletion honored via standard controls.
15) Abuse & Safety
Prompt-injection hardening: Strip/ignore instructions that attempt to override guardrails; sanitize URLs to whitelist.
Sensitive topics: Weapons/illicit/self-harm/medical/legal → do not localize; show safe global summary + official hotline/government links where applicable.
Output constraints: Regex lint blocks guarantees (“guaranteed approval”) and speculative claims.

16) Accessibility & i18n
WCAG 2.2 AA: Contrast and keyboard focus for the control; screen-reader labels (“Local Context, on/off”).
 Tested with screen-readers and keyboard navigation in v0 markets.
Script readiness: Support ₹/R$/¥, mm, Devanagari, kana rendering; truncation rules for long regulator names.
Locale variants (future): Plan for en-IN vs hi-IN toggle after v0.
17) Dependencies
Search Answers/AI Overviews; Local/Geo; Regional content (IN/BR/JP); Trust & Safety/Legal/Policy; UX Writing/Design; SRE/Infra.
18) Open Questions
Stickiness: auto-localize after first opt-in vs per-session toggle?
India variants (English vs Hindi/Hinglish) for v1?
Next intent with highest impact (banking KYC vs housing)?
Add lightweight “Report an issue” in the pilot (yes/no for v0)? Pilot with opt-in for v0 to maximize learning and user trust.
Appendix A — Evaluation Rubric (human rater)
Raters score 0–2; ship if avg ≥ 1.5 on all axes.
Axis
0
1
2
Currency/Units
Missing/incorrect
Partially correct
Fully correct, native formatting
Regulators/Permits
Absent/wrong
Named w/o link
Correct + official link
Local Trust Cues
None
One cue
Multiple relevant cues
Tone/Clarity
Generic/US-centric
Partly adapted
Feels native/concise
Freshness
No signal
Date only
Date + freshness status


Appendix B — Prompt/Model Change Log (template)
[YYYY-MM-DD] prompt_id=v03 → added “summary-only” constraint; offline accuracy +7 pts; deployed to 10% IN shadow.



Appendix C — Red-team Scenarios (examples)
Wrong regulator name; outdated fee; non-Latin script rendering; malicious prompt (“ignore sources”). Expected outcome + test steps.

