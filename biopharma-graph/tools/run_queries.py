#!/usr/bin/env python3
"""
Run the query library against a live Neo4j / Aura instance and report pass / fail per query.

    pip install neo4j                       # the only dependency; not needed for --dry-run
    cp .env.example .env                    # fill in the values Aura gave you (never commit .env)
    python3 tools/run_queries.py                         # read-only queries only
    python3 tools/run_queries.py --only Q05,Q07          # selected queries
    python3 tools/run_queries.py --section 03_traversal_lineage
    python3 tools/run_queries.py --allow-writes          # also runs write queries, then their @undo
    python3 tools/run_queries.py --dry-run               # print the statements, connect to nothing

Exit code 1 if any query fails. A query marked '@expect-error: true' passes only if it raises.
Queries marked '@skip-run' are always skipped. Always run write queries against a scratch database.
"""
import argparse, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import queries as lib

def split_statements(body):
    """Split a script on ';' that is outside quotes, backticks and comments. Comments are dropped."""
    out, cur, i, n = [], [], 0, len(body)
    q = None                                        # active quote char
    while i < n:
        c = body[i]
        if q:
            cur.append(c)
            if c == "\\" and i + 1 < n: cur.append(body[i + 1]); i += 1
            elif c == q: q = None
        elif c in "'\"`": q = c; cur.append(c)
        elif body.startswith("//", i):
            while i < n and body[i] != "\n": i += 1
            continue
        elif body.startswith("/*", i):
            j = body.find("*/", i + 2); i = n if j < 0 else j + 2; continue
        elif c == ";":
            s = "".join(cur).strip()
            if s: out.append(s)
            cur = []
        else: cur.append(c)
        i += 1
    s = "".join(cur).strip()
    if s: out.append(s)
    return out

def load_env(path):
    if not os.path.exists(path): return
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln: continue
        k, v = ln.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def select(args):
    sel = []
    only = {x.strip().upper() for x in args.only.split(",")} if args.only else None
    for s in lib.sections():
        if args.section and s["dir"] != args.section: continue
        for kind, it in s["items"]:
            if kind != "query": continue
            if only and it.id.upper() not in only: continue
            sel.append(it)
    return sel

def run_one(session, q, allow_writes):
    """returns (status, detail)"""
    f = q.fields
    if "skip-run" in f: return "SKIP", f["skip-run"]
    if q.writes and not allow_writes: return "SKIP", "writes data (use --allow-writes on a scratch database)"
    expect_err = f.get("expect-error", "").lower() == "true"
    t0 = time.time(); rows = 0; err = None
    try:
        for stmt in split_statements(q.body):
            res = session.run(stmt); rows += sum(1 for _ in res); res.consume()
    except Exception as ex:                       # noqa: BLE001 - we report any driver error
        err = ex
    finally:
        undo = f.get("undo", "")
        if q.writes and undo and not undo.lower().startswith("none"):
            for stmt in split_statements(undo): session.run(stmt).consume()
    dt = time.time() - t0
    if expect_err: return ("PASS", f"raised as expected: {str(err).splitlines()[0][:90]}") if err else ("FAIL", "expected an error but it succeeded")
    if err: return "FAIL", str(err).splitlines()[0][:200]
    return "PASS", f"{rows} rows, {dt:.2f}s"

def main(argv=None, driver_factory=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only"); ap.add_argument("--section"); ap.add_argument("--allow-writes", action="store_true")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--env", default=os.path.join(lib.ROOT, ".env"))
    args = ap.parse_args(argv)
    qs = select(args)
    if not qs: print("no queries selected"); return 1
    if args.dry_run:
        for q in qs:
            print(f"-- {q.id} {q.fields.get('title','')}  (writes={q.writes})")
            for s in split_statements(q.body): print("   " + s.replace("\n", "\n   ") + ";")
        return 0
    load_env(args.env)
    uri, user, pw = os.environ.get("NEO4J_URI"), os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER"), os.environ.get("NEO4J_PASSWORD")
    db = os.environ.get("NEO4J_DATABASE", "neo4j")
    if not (uri and user and pw): sys.exit("set NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD (see .env.example)")
    if driver_factory is None:
        try: from neo4j import GraphDatabase
        except ImportError: sys.exit("pip install neo4j   (or use --dry-run)")
        driver_factory = lambda: GraphDatabase.driver(uri, auth=(user, pw))
    failed = 0
    with driver_factory() as driver:
        driver.verify_connectivity()
        with driver.session(database=db) as session:
            for q in qs:
                status, detail = run_one(session, q, args.allow_writes)
                failed += status == "FAIL"
                print(f"{status:<5} {q.id:<4} {q.fields.get('title','')[:48]:<48} {detail}")
    print(f"\n{len(qs)} selected, {failed} failed"); return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
