"""Generates reset.cypher and post_load.cypher from spec.py (+ row counts from the CSVs).
   python3 -I make_cypher.py <csv_dir> <out_dir>"""
import csv, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import spec
csv_dir, out = sys.argv[1], sys.argv[2]
LEGACY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model", "legacy_v1_names.json")
def nrows(f): return sum(1 for _ in open(os.path.join(csv_dir, f), encoding="utf-8")) - 1

# ---------------------------------------------------------------- reset
v1c, v1i = [], []
if os.path.exists(LEGACY):
    _l = json.load(open(LEGACY)); v1c, v1i = _l["constraints"], _l["indexes"]
v2c = [f"{l}_{p}_unique" for l, n in spec.NODES.items() for p in [n["key"]] + n.get("unique", [])]
L = ["// reset.cypher - wipe a half-loaded database so the importer starts from a clean slate.",
     "// Run in Aura 'Query'. Safe to run repeatedly (IF EXISTS everywhere).",
     "// ORDER MATTERS: constraints first (this also removes their backing indexes), then data.", "",
     "// 0) FIND constraints/indexes this script does not know by name (e.g. created by hand or by an earlier tool).",
     "//    Run each of these two queries on its own, then copy the generated DROP statements from the result column and run them.",
     "SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties RETURN name, type, labelsOrTypes, properties ORDER BY labelsOrTypes;",
     "SHOW CONSTRAINTS YIELD name RETURN 'DROP CONSTRAINT `' + name + '` IF EXISTS;' AS runThese;",
     "SHOW INDEXES YIELD name, type WHERE type <> 'LOOKUP' RETURN 'DROP INDEX `' + name + '` IF EXISTS;' AS runThese;", "",
     "// 1) constraints + indexes left behind by the ORIGINAL (v1) model"]
L += [f"DROP CONSTRAINT `{n}` IF EXISTS;" for n in dict.fromkeys(v1c)]
L += [f"DROP INDEX `{n}` IF EXISTS;" for n in dict.fromkeys(v1i)]
L += ["", "// 2) constraints left behind by this (v2) model"] + [f"DROP CONSTRAINT `{n}` IF EXISTS;" for n in v2c]
L += ["", "// 3) optional objects from post_load.cypher"]
L += [f"DROP CONSTRAINT `{l}_{p}_exists` IF EXISTS;" for l, n in spec.NODES.items() for p, t, req in n["props"] if req]
IDX = [("Batch", "status"), ("Batch", "gmpStatus"), ("TestResult", "outcome"), ("TestResult", "testedAt"), ("TestResult", "reviewStatus"),
       ("Sample", "samplePoint"), ("Deviation", "status"), ("MaterialLot", "status"), ("Specification", "attribute"), ("StepExecution", "status")]
L += [f"DROP INDEX `{l}_{p}_idx` IF EXISTS;" for l, p in IDX]
L += ["", "// 4) data (fine for this size; for >100k nodes use CALL { ... } IN TRANSACTIONS)", "MATCH (n) DETACH DELETE n;", "",
      "// 5) verify - expect: no constraints, no indexes except the default LOOKUP indexes, 0 nodes", "SHOW CONSTRAINTS;", "SHOW INDEXES;", "MATCH (n) RETURN count(n) AS nodesLeft;"]
open(os.path.join(out, "reset.cypher"), "w").write("\n".join(L) + "\n")

# ---------------------------------------------------------------- post load
P = ["// post_load.cypher - run AFTER the importer finishes. Everything is idempotent (IF NOT EXISTS).", "",
     "// ===== A. Row-count verification (compare with the numbers in the comments) =====",
     "MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS nodes ORDER BY label;"]
P += [f"//   {l:<22} {nrows(n['file'])}" for l, n in spec.NODES.items()]
P += ["MATCH ()-[r]->() RETURN type(r) AS relationship, count(*) AS rels ORDER BY relationship;"]
P += [f"//   {r['type']:<22} {nrows(r['file'])}" for r in spec.RELS]
P += ["", "// ===== B. Optional: NOT NULL (existence) constraints =====",
      "// Property existence constraints are an Enterprise feature; if your tier rejects them, skip this block - the importer",
      "// mapping + validate.py already guarantee required values.  (They were part of the original model and are NOT in the importer file.)"]
P += [f"CREATE CONSTRAINT `{l}_{p}_exists` IF NOT EXISTS FOR (n:{l}) REQUIRE n.{p} IS NOT NULL;" for l, n in spec.NODES.items() for p, t, req in n["props"] if req]
P += ["", "// ===== C. Lookup indexes for the common questions (named *_idx so they can never collide with a constraint) ====="]
P += [f"CREATE INDEX `{l}_{p}_idx` IF NOT EXISTS FOR (n:{l}) ON (n.{p});" for l, p in IDX]
P += ["", "// Example queries live in queries/ (see README)."]
open(os.path.join(out, "post_load.cypher"), "w").write("\n".join(P) + "\n")
print("wrote reset.cypher (%d statements) and post_load.cypher" % (len(L)))
