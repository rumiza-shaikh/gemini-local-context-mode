import sys, yaml, re, glob

REQ_TOP = ["country","version","updated_at","currency","units","tone",
           "regulatory_refs","freshness","rewrite_rules","guardrails"]

def lint_pack(path):
    errs=[]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"YAML load error: {e}"]

    for k in REQ_TOP:
        if k not in data:
            errs.append(f"missing `{k}`")

    # updated_at ISO
    try:
        if not re.match(r"\d{4}-\d{2}-\d{2}T", data.get("updated_at","")):
            errs.append("`updated_at` must be ISO-8601 e.g., 2025-08-12T00:00:00Z")
    except Exception:
        errs.append("`updated_at` invalid")

    # regulatory_refs
    refs = data.get("regulatory_refs", [])
    if not refs:
        errs.append("no regulatory_refs[]")
    else:
        for i, r in enumerate(refs):
            for k in ["name","url","disclaimer"]:
                if k not in r:
                    errs.append(f"regulatory_refs[{i}] missing `{k}`")

    # freshness
    fr = data.get("freshness", {})
    if fr.get("sla_days", 0) > 30:
        errs.append("freshness.sla_days > 30 (too high for demo SLA)")
    if not fr.get("watchers"):
        errs.append("freshness.watchers[] required")

    # rewrite_rules + guardrails quick checks
    rrs = data.get("rewrite_rules", [])
    if not rrs:
        errs.append("no rewrite_rules[]")
    forb = set(map(str.lower, data.get("guardrails",{}).get("forbidden_claims",[])))
    for rr in rrs:
        for b in rr.get("summary", []):
            bl = b.lower()
            for bad in forb:
                if bad and bad in bl:
                    errs.append(f"forbidden claim found in summary: '{bad}'")

    return errs

if __name__ == "__main__":
    paths = glob.glob("packs/*.yaml")
    failed = False
    if not paths:
        print("No packs found in packs/*.yaml")
        sys.exit(1)
    for p in paths:
        e = lint_pack(p)
        if e:
            failed = True
            print(f"[FAIL] {p}")
            for x in e: print("  -", x)
        else:
            print(f"[OK]   {p}")
    sys.exit(1 if failed else 0)
