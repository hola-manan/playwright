#!/usr/bin/env python3
"""Verify the module decomposition.

Checks that the module index, the spec files, and the repo scaffold agree, that
no spec references a module that does not exist, and that tier dependency
direction is respected.

Run from the repo root:  python3 tools/check_modules.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "docs" / "modules"
INDEX = SPEC_DIR / "README.md"

ID_RE = re.compile(r"\b([FEBCP]\d{2})\b")
EXPECTED_COUNT = 69

failures = []
notes = []


def fail(check, msg):
    failures.append(f"[{check}] {msg}")


def section(text, heading):
    """Return the body of a '## heading' section, up to the next '## '."""
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text,
                  re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- load specs
specs = {}
for p in sorted(SPEC_DIR.glob("*.md")):
    if p.name in ("README.md", "_TEMPLATE.md"):
        continue
    m = re.match(r"([FEBCP]\d{2})-(.+)\.md$", p.name)
    if not m:
        fail("naming", f"{p.name} does not match <ID>-<name>.md")
        continue
    specs[m.group(1)] = {"path": p, "name": m.group(2), "text": p.read_text()}

# ---------------------------------------------- check 2: index <-> files agree
index_text = INDEX.read_text()
index_ids = set()
for line in index_text.splitlines():
    m = re.match(r"\|\s*\[([FEBCP]\d{2})\]\(", line)
    if m:
        index_ids.add(m.group(1))

if len(specs) != EXPECTED_COUNT:
    fail("2 index<->files", f"found {len(specs)} spec files, expected {EXPECTED_COUNT}")
if len(index_ids) != EXPECTED_COUNT:
    fail("2 index<->files", f"index lists {len(index_ids)} modules, expected {EXPECTED_COUNT}")
for missing in sorted(set(specs) - index_ids):
    fail("2 index<->files", f"{missing} has a spec but is not in the index table")
for missing in sorted(index_ids - set(specs)):
    fail("2 index<->files", f"{missing} is in the index table but has no spec file")

# ------------------------------------------- check 3: dependencies & direction
TIER_OF = lambda mid: mid[0]
# Engines may use client *core* (C01-C04) but never a client feature screen.
CLIENT_FEATURES = {f"C{n:02d}" for n in range(5, 20)}
# The tier rule exists to keep the *request path* acyclic. Two pedagogy modules
# are offline pipelines rather than request-path participants: P12 ingestion runs
# on a schedule and P17 eval drives the pipeline it scores. Both legitimately use
# shared backend clients, so both are exempt. P13 retrieval IS on the request path
# and is deliberately not exempt.
PEDAGOGY_OFFLINE = {"P12", "P17"}

for mid, spec in sorted(specs.items()):
    deps = set(ID_RE.findall(section(spec["text"], "Depends on"))) - {mid}
    rdeps = set(ID_RE.findall(section(spec["text"], "Depended on by"))) - {mid}

    for ref in sorted(deps | rdeps):
        if ref not in specs:
            fail("3 dangling", f"{mid} references {ref}, which does not exist")

    tier = TIER_OF(mid)
    for d in sorted(deps):
        dt = TIER_OF(d)
        if tier == "B" and dt in ("C", "E"):
            fail("3 direction", f"{mid} (backend) depends on {d} (tier {dt})")
        if tier == "E" and d in CLIENT_FEATURES:
            fail("3 direction", f"{mid} (engine) depends on client feature {d}")
        if tier == "F" and dt in ("C", "E", "P"):
            fail("3 direction", f"{mid} (foundation) depends on {d} (tier {dt})")
        if tier == "P" and dt in ("B", "C", "E") and mid not in PEDAGOGY_OFFLINE:
            fail("3 direction", f"{mid} (pedagogy) depends on {d} (tier {dt})")

# ------------------------------------------- check 5: no orphaned ownership
# Every "→ `Pxx`" arrow in a "Does not own" block must land on a module that
# actually claims that responsibility under "Owns". This is what proves a scope
# transfer happened rather than merely being declared.
for mid, spec in sorted(specs.items()):
    scope = section(spec["text"], "Scope")
    if "**Does not own**" not in scope:
        continue
    disowned = scope.split("**Does not own**", 1)[1]
    for ref in sorted(set(ID_RE.findall(disowned))):
        if ref == mid:
            fail("5 orphan", f"{mid} disowns something to itself")
        elif ref not in specs:
            fail("5 orphan", f"{mid} disowns to {ref}, which does not exist")
        else:
            owns = section(specs[ref]["text"], "Scope")
            if "**Owns**" not in owns:
                fail("5 orphan",
                     f"{mid} disowns to {ref}, but {ref} has no Owns block")

# ------------------------------------------------- check 4: source references
for mid, spec in sorted(specs.items()):
    refs = section(spec["text"], "Source references")
    if not refs.strip():
        fail("4 coverage", f"{mid} has no Source references section")
    elif not re.search(r"(FEATURE_PLAN|ARCHITECTURE)\.md", refs):
        fail("4 coverage", f"{mid} cites neither source document")

# -------------------------------------------- check 6: scaffold matches specs
scaffold_dirs = set()
for mid, spec in sorted(specs.items()):
    m = re.search(r"^\*\*Code location:\*\*\s*`([^`]+)`", spec["text"], re.MULTILINE)
    if not m:
        if mid != "E06":
            fail("6 scaffold", f"{mid} has no Code location")
        continue
    loc = m.group(1).rstrip("/")
    if loc.startswith("docs/") or loc == "this document":
        continue
    d = ROOT / loc
    if not d.is_dir():
        fail("6 scaffold", f"{mid} Code location `{loc}` does not exist on disk")
    elif not (d / "README.md").is_file():
        fail("6 scaffold", f"{mid} folder `{loc}` has no README stub")
    else:
        scaffold_dirs.add(d.resolve())

for area in ("apps", "services", "packages", "infra"):
    for readme in (ROOT / area).rglob("README.md"):
        if readme.parent.resolve() not in scaffold_dirs:
            fail("6 scaffold", f"stub {readme.relative_to(ROOT)} maps to no module")

# ------------------------------------- check 6b: build order schedules all 69
BUILD_ORDER = ROOT / "docs" / "BUILD_ORDER.md"
if not BUILD_ORDER.is_file():
    fail("6b build order", "docs/BUILD_ORDER.md is missing")
else:
    bo_text = BUILD_ORDER.read_text()
    scheduled = set(ID_RE.findall(bo_text))
    for ref in sorted(scheduled):
        if ref not in specs:
            fail("6b build order", f"BUILD_ORDER.md references {ref}, which does not exist")
    for missing in sorted(set(specs) - scheduled):
        fail("6b build order", f"{missing} appears in no phase — silently unscheduled")
    notes.append(f"build order schedules {len(scheduled & set(specs))} modules")

# --------------------------------------------------- check 7: mermaid fences
opens = len(re.findall(r"^```mermaid\s*$", index_text, re.MULTILINE))
fences = len(re.findall(r"^```", index_text, re.MULTILINE))
if opens == 0:
    fail("7 mermaid", "index contains no mermaid diagram")
if fences % 2 != 0:
    fail("7 mermaid", "unbalanced code fences in the index")
notes.append(f"index contains {opens} mermaid diagram(s)")

# ------------------------------------------------------------------- report
print(f"modules: {len(specs)}  index rows: {len(index_ids)}  "
      f"scaffold folders: {len(scaffold_dirs)}")
for n in notes:
    print(f"  note: {n}")

if failures:
    print(f"\nFAILED — {len(failures)} problem(s):")
    for f in failures:
        print(f"  {f}")
    sys.exit(1)

print("\nAll checks passed.")
