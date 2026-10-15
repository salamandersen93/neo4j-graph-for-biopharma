"""
Static lint for an Aura Data Importer model file (works on v1 and v2).
    python3 -I check_importer_json.py <model.json> [<csv_dir>]
Catches the problems that surface as 'uniqueness' / 'already exists' errors in the console,
plus dangling $refs and CSV/mapping drift.
"""
import json, sys, os, csv
from collections import Counter
m = json.load(open(sys.argv[1])); d = m["dataModel"]; gs = d["graphSchemaRepresentation"]["graphSchema"]
csv_dir = sys.argv[2] if len(sys.argv) > 2 else None
errs, warns = [], []
ids = []
def walk(o):
    if isinstance(o, dict):
        if "$id" in o: ids.append(o["$id"])
        [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
walk(d)
errs += [f"duplicate $id {i}" for i, c in Counter(ids).items() if c > 1]
def refs(o):
    if isinstance(o, dict):
        if "$ref" in o: yield o["$ref"][1:]
        for v in o.values(): yield from refs(v)
    elif isinstance(o, list):
        for v in o: yield from refs(v)
idset = set(ids)
errs += [f"dangling $ref {r}" for r in set(refs(d)) if r not in idset]
# schema-object name collisions (the v1 bug)
cn = Counter(c["name"] for c in gs["constraints"]); xn = Counter(i["name"] for i in gs["indexes"])
errs += [f"constraint name used twice: {n}" for n, c in cn.items() if c > 1]
errs += [f"index name used twice: {n}" for n, c in xn.items() if c > 1]
errs += [f"index and constraint share the name '{n}'  -> 'already exists' error on CREATE" for n in set(cn) & set(xn)]
# an index on the same label+property set as a uniqueness constraint is redundant (equivalent index already exists)
def sig(o): return (o["nodeLabel"]["$ref"], tuple(p["$ref"] for p in o["properties"]))
uniq = {sig(c) for c in gs["constraints"] if c["constraintType"] == "uniqueness"}
errs += [f"index '{i['name']}' duplicates the backing index of a uniqueness constraint" for i in gs["indexes"] if sig(i) in uniq]
# multiple uniqueness constraints on same label+props
dups = Counter(sig(c) for c in gs["constraints"] if c["constraintType"] == "uniqueness")
errs += [f"uniqueness constraint declared twice on {s}" for s, c in dups.items() if c > 1]
ex = [c for c in gs["constraints"] if c["constraintType"] != "uniqueness"]
if ex: warns.append(f"{len(ex)} non-uniqueness constraints in model ({Counter(c['constraintType'] for c in ex)}); existence/key constraints are Enterprise-only on some tiers")
# mappings
tabs = {t["$id"]: t for t in d["graphMappingRepresentation"]["dataSourceSchema"]["tableSchemas"]}
props = {}
for l in gs["nodeLabels"] + gs["relationshipTypes"]:
    for p in l["properties"]: props[p["$id"]] = (l["token"], p["token"])
keys = {k["node"]["$ref"][1:]: k["keyProperty"]["$ref"][1:] for k in d["graphSchemaExtensionsRepresentation"]["nodeKeyProperties"]}
for nm in d["graphMappingRepresentation"]["nodeMappings"]:
    t = tabs[nm["tableSchema"]["$ref"][1:]]; mapped = {x["property"]["$ref"][1:] for x in nm["propertyMappings"]}
    fields = {f["name"] for f in t["fields"]}
    errs += [f"{t['name']}: mapping column {x['fieldName']} not in table fields" for x in nm["propertyMappings"] if x["fieldName"] not in fields]
    if keys.get(nm["node"]["$ref"][1:]) not in mapped: errs.append(f"{t['name']}: key property not mapped")
nodefile = {}
for nm in d["graphMappingRepresentation"]["nodeMappings"]: nodefile[nm["node"]["$ref"][1:]] = tabs[nm["tableSchema"]["$ref"][1:]]
for rm in d["graphMappingRepresentation"]["relationshipMappings"]:
    t = tabs[rm["tableSchema"]["$ref"][1:]]; fields = {f["name"] for f in t["fields"]}
    for k in ("fromMapping", "toMapping"):
        if rm[k]["fieldName"] not in fields: errs.append(f"{t['name']}: {k} column {rm[k]['fieldName']} missing")
    if rm["fromMapping"]["fieldName"] == rm["toMapping"]["fieldName"]: errs.append(f"{t['name']}: from and to use the same column")
if csv_dir:
    for t in tabs.values():
        p = os.path.join(csv_dir, t["name"])
        if not os.path.exists(p): errs.append(f"missing CSV {t['name']}"); continue
        hdr = next(csv.reader(open(p, encoding="utf-8-sig")))
        if hdr != [f["name"] for f in t["fields"]]: errs.append(f"{t['name']}: CSV header {hdr} != model fields")
    mapped_tables = {nm["tableSchema"]["$ref"][1:] for nm in d["graphMappingRepresentation"]["nodeMappings"]} | {rm["tableSchema"]["$ref"][1:] for rm in d["graphMappingRepresentation"]["relationshipMappings"]}
    warns += [f"table {t['name']} is not mapped" for i, t in tabs.items() if i not in mapped_tables]
for w in warns: print("WARN ", w)
for e in errs: print("ERROR", e)
print(f"{len(errs)} error(s), {len(warns)} warning(s) - {os.path.basename(sys.argv[1])}")
sys.exit(1 if errs else 0)
