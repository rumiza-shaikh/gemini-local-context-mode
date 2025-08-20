# Guardrails

## Scope & Non-Goals
- Provide **market context** (currency, examples, summary compliance cues).
- Not legal/medical/financial advice. No guarantees of approval.

## Language & Claims
- Use hedged phrasing: “may require…”, “typically…”
- **Forbidden**: “legal advice”, “guaranteed approval”, “will be accepted”

## Staleness & Sources
- Each locale must include:
  - `updated_at` (ISO-8601)
  - `regulatory_refs[]` with `name`, `url`, `disclaimer`
  - `freshness.watchers[]` + `freshness.sla_days`
- UI shows: “Updated <date> • Freshness checked X day(s) ago”
- Link to official sources; no paraphrase without link-out

## Abuse & Safety Exclusions
- Do not localize illegal/unsafe queries (weapons, self-harm, illicit activity)
- Fallback to global safe summary with warning

## Rollback Triggers
- >1% sessions flagged for incorrect/dated compliance cues
- CTR/quality regressions per experiment gates
- Any P0 bug → disable flag immediately

## Observability
- Log guardrail flags, variant, market, intent
- Daily review: freshness queue, flagged sessions, CTR deltas
