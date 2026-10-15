#!/usr/bin/env python3
"""
Query library tooling: parse, lint, and render the queries/ tree.

    python3 -I tools/queries.py lint            # structure + schema-aware checks (CI runs this)
    python3 -I tools/queries.py docs            # writes docs/queries.md and dist/all_queries.cypher
    python3 -I tools/queries.py list            # one line per query
    python3 -I tools/queries.py new <section> <slug> "<Title>"   # scaffold the next Qnn in a section

Layout   queries/<NN_section>/_section.md          section title + intro prose (markdown)
         queries/<NN_section>/qNN_<slug>.cypher    one query (or a small script) with a header block
         queries/<NN_section>/qNNa_<slug>.md       interstitial note, rendered after qNN, before qNN+1
Header   '// @field: value' lines (continuation lines are plain '//' comments), ended by '// ---'
"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "model"))
import spec

QDIR = os.path.join(ROOT, "queries")
REQUIRED = ["id", "title", "level", "writes", "learn", "biopharma", "expect"]
LEVELS = {"beginner", "intermediate", "advanced"}
KNOWN_FIELDS = set(REQUIRED) | {"neo4j", "undo", "skip-run", "expect-error"}

class Query:
    def __init__(self, path, section):
        self.path, self.section = path, section
        self.file = os.path.basename(path)
        self.fields, self.body, self.errors = {}, "", []
        self._parse()
    def _parse(self):
        with open(self.path, encoding="utf-8") as fh: lines = fh.read().splitlines()
        cur = None; i = 0
        while i < len(lines):
            ln = lines[i]
            if ln.strip() == "// ---": i += 1; break
            m = re.match(r"//\s*@([\w-]+):\s*(.*)$", ln)
            if m: cur = m.group(1); self.fields[cur] = m.group(2).strip()
            elif ln.startswith("//") and cur: self.fields[cur] += "\n" + re.sub(r"^//\s?", "", ln)
            elif ln.strip() == "": cur = None
            else: self.errors.append(f"line {i+1}: unexpected content before '// ---' separator"); break
            i += 1
        else:
            self.errors.append("missing '// ---' separator after header")
        self.body = "\n".join(lines[i:]).strip("\n")
        for k in list(self.fields):
            v = self.fields[k].strip()
            # prose fields: join wrapped lines with single spaces; @undo keeps its line breaks (it is code)
            self.fields[k] = v if k == "undo" else " ".join(x.strip() for x in v.split("\n") if x.strip())
    @property
    def id(self): return self.fields.get("id", "")
    @property
    def writes(self): return self.fields.get("writes", "").lower() == "true"

def sections():
    out = []
    for d in sorted(os.listdir(QDIR)):
        p = os.path.join(QDIR, d)
        if not os.path.isdir(p) or d.startswith((".", "_")): continue
        intro = os.path.join(p, "_section.md")
        title, body = d, ""
        if os.path.exists(intro):
            with open(intro, encoding="utf-8") as fh: txt = fh.read().strip().splitlines()
            if txt and txt[0].startswith("# "): title, body = txt[0][2:].strip(), "\n".join(txt[1:]).strip()
            else: body = "\n".join(txt)
        items = []
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            if f.endswith(".cypher"): items.append(("query", Query(fp, d)))
            elif f.endswith(".md") and f != "_section.md": items.append(("note", fp))
        out.append(dict(dir=d, title=title, intro=body, items=items, has_intro=os.path.exists(intro)))
    return out

# ---------------------------------------------------------------- lint
def strip(body):
    body = re.sub(r"//[^\n]*", "", body)                       # line comments
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)           # block comments
    return re.sub(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", "''", body)   # string literals
def schema_names():
    labels = set(spec.NODES); rels = {r["type"] for r in spec.RELS}
    props = {p[0] for n in spec.NODES.values() for p in n["props"]} | {p[0] for r in spec.RELS for p in r["props"]}
    return labels, rels, props
# names that are legal in queries but not part of the model (used by SHOW output, scratch nodes from write examples ...)
ALLOWED_EXTRA_PROPS = {"lastTouched", "created", "labelsOrTypes", "properties", "name", "type"}
def lint():
    errs, warns = [], []
    labels, rels, props = schema_names()
    seen = {}
    secs = sections()
    if not secs: errs.append("queries/ has no sections")
    for s in secs:
        if not s["has_intro"]: errs.append(f"{s['dir']}: missing _section.md")
        for kind, it in s["items"]:
            if kind == "note":
                if not re.match(r"q\d+[a-z]_", os.path.basename(it)): errs.append(f"{s['dir']}/{os.path.basename(it)}: notes must be named qNNa_*.md (placed after qNN)")
                continue
            q = it; where = f"{q.section}/{q.file}"
            errs += [f"{where}: {e}" for e in q.errors]
            for k in REQUIRED:
                if not q.fields.get(k): errs.append(f"{where}: missing @{k}")
            for k in q.fields:
                if k not in KNOWN_FIELDS: errs.append(f"{where}: unknown field @{k}")
            fid = re.match(r"(q\d+)_", q.file)
            if not fid: errs.append(f"{where}: file name must start with qNN_")
            elif q.id.lower() != fid.group(1): errs.append(f"{where}: @id {q.id!r} does not match file prefix {fid.group(1)!r}")
            if q.id in seen: errs.append(f"{where}: duplicate id {q.id} (also {seen[q.id]})")
            seen[q.id] = where
            if q.fields.get("level") and q.fields["level"] not in LEVELS: errs.append(f"{where}: @level must be one of {sorted(LEVELS)}")
            if q.fields.get("writes", "").lower() not in ("true", "false"): errs.append(f"{where}: @writes must be true or false")
            if q.writes and not q.fields.get("undo"): errs.append(f"{where}: @writes: true needs an @undo (statements, or 'none: <reason>')")
            if not q.body.strip(): errs.append(f"{where}: empty query body"); continue
            code = strip(q.body)
            if True:
                for lab in set(re.findall(r"\(\s*\w*\s*:\s*`?([A-Za-z_]\w*)", code)):
                    if lab not in labels: errs.append(f"{where}: unknown label :{lab}")
                for rel_ in set(t for grp in re.findall(r"\[\s*\w*\s*:\s*([A-Za-z_][\w|:]*)", code) for t in re.split(r"[|:]", grp) if t):
                    if rel_ not in rels: errs.append(f"{where}: unknown relationship type :{rel_}")
                for key in set(re.findall(r"[{,]\s*(\w+)\s*:", code)):
                    if key not in props and key not in ALLOWED_EXTRA_PROPS: errs.append(f"{where}: unknown property key '{key}' in a map")
            if not q.writes and re.search(r"\b(CREATE|MERGE|DELETE|REMOVE|DROP)\b|\bSET\s", code):
                errs.append(f"{where}: @writes: false but the body contains a write keyword")
    return errs, warns

# ---------------------------------------------------------------- render
def render():
    md = ["# Query library", "",
          "_Generated by `tools/queries.py docs` from the files in `queries/` - do not edit by hand._", ""]
    toc, body = [], []
    flat = []
    for s in sections():
        body += [f"## {s['title']}", ""]
        if s["intro"]: body += [s["intro"], ""]
        toc.append(f"- **{s['title']}**")
        for kind, it in s["items"]:
            if kind == "note":
                with open(it, encoding="utf-8") as fh: body += [fh.read().strip(), ""]
                continue
            q = it; f = q.fields
            toc.append(f"  - {q.id} - {f.get('title','')}")
            flat.append(q)
            badge = f"`{f.get('level','?')}`" + ("  `writes data`" if q.writes else "  `read-only`") + (f"  `needs Neo4j {f['neo4j']}`" if f.get("neo4j") and f["neo4j"] != "5.x" else "")
            body += [f"### {q.id} - {f.get('title','')}", "", badge, "",
                     f"**What you learn.** {f.get('learn','')}", "",
                     f"**Why it matters in biopharma.** {f.get('biopharma','')}", "",
                     "```cypher", q.body, "```", "",
                     f"**What to expect.** {f.get('expect','')}", ""]
            if q.writes: body += ["**Undo.**", "```cypher", f.get("undo", ""), "```", ""]
    return "\n".join(md + ["## Contents", ""] + toc + [""] + body).rstrip() + "\n", flat
def write_docs():
    text, flat = render()
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True); os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "queries.md"), "w", encoding="utf-8").write(text)
    allq = ["// all_queries.cypher - every query in the library, in order. Generated; do not edit.", ""]
    for q in flat:
        allq += [f"// ===== {q.id} - {q.fields.get('title','')}  [{q.section}] =====", q.body, ""]
    open(os.path.join(ROOT, "dist", "all_queries.cypher"), "w", encoding="utf-8").write("\n".join(allq))
    print(f"docs/queries.md and dist/all_queries.cypher written ({len(flat)} queries)")

def new(section, slug, title):
    d = os.path.join(QDIR, section)
    if not os.path.isdir(d): sys.exit(f"no such section folder: queries/{section}  (create it with a _section.md first)")
    ids = [int(m.group(1)) for _, it in [(k, v) for s in sections() for k, v in s["items"]] if hasattr(it, "file") for m in [re.match(r"q(\d+)_", it.file)] if m]
    n = max(ids or [0]) + 1; qid = f"Q{n:02d}"; path = os.path.join(d, f"q{n:02d}_{slug}.cypher")
    open(path, "w", encoding="utf-8").write(f"""// @id: {qid}
// @title: {title}
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: One sentence on the Cypher concept this query teaches.
// @biopharma: Where this question comes up in drug development / manufacturing / QC, and why a graph answers it well.
// @expect: What the result should look like on the loaded dataset (row counts, notable values).
// ---
MATCH (n) RETURN count(n) AS nodes;
""")
    print("created", os.path.relpath(path, ROOT))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lint"
    if cmd == "lint":
        e, w = lint()
        for x in w: print("WARN ", x)
        for x in e: print("ERROR", x)
        n = sum(1 for s in sections() for k, _ in s["items"] if k == "query")
        print(f"{n} queries in {len(sections())} sections: {len(e)} error(s), {len(w)} warning(s)"); sys.exit(1 if e else 0)
    elif cmd == "docs": write_docs()
    elif cmd == "list":
        for s in sections():
            for k, it in s["items"]:
                if k == "query": print(f"{it.id:<4} {s['dir']:<26} {it.fields.get('level',''):<12} {'W' if it.writes else ' '} {it.fields.get('title','')}")
    elif cmd == "new": new(*sys.argv[2:5])
    else: sys.exit(__doc__)
