"""
Builds neo4j_importer_model.json (Aura Data Importer format, same structure as the original export)
directly from spec.py + the CSVs (for field samples).   Usage: python3 -I build_importer_json.py <csv_dir> <out.json>

Design rules that prevent the v1 failures:
  * ONE uniqueness constraint per key (+ e-mail), unique names, and NO standalone index objects
    (a uniqueness constraint already creates its backing index; a same-named index collides).
  * No existence constraints in the model (Enterprise-only on some Aura tiers; they live in post_load.cypher).
  * Column name == property name, so nothing can be mapped to the wrong property.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import spec

POS = {  # x, y grid (drag around in the UI to taste)
 "CellBank": (0, 0), "Product": (500, 0), "Specification": (1000, 0), "Assay": (1500, 0), "Instrument": (2000, 0),
 "Bioreactor": (0, 450), "Batch": (500, 450), "Sample": (1000, 450), "TestResult": (1500, 450), "Lab": (2000, 450),
 "MaterialLot": (0, 900), "PurificationProtocol": (500, 900), "StepExecution": (1000, 900), "Employee": (1500, 900), "Deviation": (2000, 900),
 "Material": (0, 1350), "PurificationStep": (500, 1350),
}

def build(csv_dir):
    nid = {l: f"n{i}" for i, l in enumerate(spec.NODES)}
    pcount = [0]; props = {}                          # (label|type, prop) -> $id
    def pid(owner, name):
        pcount[0] += 1; props[(owner, name)] = f"p:{pcount[0]}"; return props[(owner, name)]
    nodeLabels, nodeObjs, tables, nodeMaps = [], [], [], []
    def sample(file, col):
        with open(os.path.join(csv_dir, file), newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row[col] != "": return row[col]
        return ""
    tcount = 0
    for label, n in spec.NODES.items():
        nodeLabels.append({"$id": f"nl:{nid[label]}", "token": label, "properties": [
            {"$id": pid(label, p), "token": p, "type": {"type": t}, "nullable": not req} for p, t, req in n["props"]]})
        nodeObjs.append({"$id": f"n:{nid[label]}", "labels": [{"$ref": f"#nl:{nid[label]}"}]})
        tcount += 1
        tables.append({"$id": f"t:{tcount}", "name": n["file"], "expanded": True,
                       "fields": [{"name": p, "type": t, "sample": sample(n["file"], p), "include": True} for p, t, _ in n["props"]]})
        nodeMaps.append({"node": {"$ref": f"#n:{nid[label]}"}, "tableSchema": {"$ref": f"#t:{tcount}"},
                         "propertyMappings": [{"fieldName": p, "property": {"$ref": "#" + props[(label, p)]}} for p, _, _ in n["props"]]})
    relTypes, relObjs, relMaps, graphRels = [], [], [], []
    for i, r in enumerate(spec.RELS):
        rid = f"n{i}"; fc, tc = spec.rel_cols(r)
        relTypes.append({"$id": f"rt:{rid}", "token": r["type"], "properties": [
            {"$id": pid(r["type"], p), "token": p, "type": {"type": t}, "nullable": not req} for p, t, req in r["props"]]})
        relObjs.append({"$id": f"r:{rid}", "type": {"$ref": f"#rt:{rid}"}, "from": {"$ref": f"#n:{nid[r['frm']]}"}, "to": {"$ref": f"#n:{nid[r['to']]}"}})
        graphRels.append({"id": rid, "type": r["type"], "fromId": nid[r["frm"]], "toId": nid[r["to"]]})
        tcount += 1
        fields = [(fc, "string"), (tc, "string")] + [(p, t) for p, t, _ in r["props"]]
        tables.append({"$id": f"t:{tcount}", "name": r["file"], "expanded": True,
                       "fields": [{"name": c, "type": t, "sample": sample(r["file"], c), "include": True} for c, t in fields]})
        relMaps.append({"relationship": {"$ref": f"#r:{rid}"}, "tableSchema": {"$ref": f"#t:{tcount}"},
                        "propertyMappings": [{"fieldName": p, "property": {"$ref": "#" + props[(r["type"], p)]}} for p, _, _ in r["props"]],
                        "fromMapping": {"fieldName": fc}, "toMapping": {"fieldName": tc}})
    constraints = []
    for label, n in spec.NODES.items():
        for prop in [n["key"]] + n.get("unique", []):
            constraints.append({"$id": f"c:{len(constraints)+1}", "name": f"{label}_{prop}_unique", "constraintType": "uniqueness",
                                "entityType": "node", "nodeLabel": {"$ref": f"#nl:{nid[label]}"}, "properties": [{"$ref": "#" + props[(label, prop)]}]})
    names = [c["name"] for c in constraints]; assert len(names) == len(set(names))
    return {
     "version": "1.4.0-beta.0",
     "graph": {"nodes": [{"id": nid[l], "position": {"x": POS[l][0], "y": POS[l][1]}, "caption": l} for l in spec.NODES], "relationships": graphRels},
     "dataModel": {
      "version": "1.4.0-beta.0",
      "graphSchemaRepresentation": {"version": "1.0.0", "graphSchema": {
          "nodeLabels": nodeLabels, "relationshipTypes": relTypes, "nodeObjectTypes": nodeObjs, "relationshipObjectTypes": relObjs,
          "constraints": constraints, "indexes": []}},
      "graphSchemaExtensionsRepresentation": {"nodeKeyProperties": [
          {"node": {"$ref": f"#n:{nid[l]}"}, "keyProperty": {"$ref": "#" + props[(l, n["key"])]}} for l, n in spec.NODES.items()]},
      "graphMappingRepresentation": {"dataSourceSchema": {"type": "local/csv", "tableSchemas": tables},
                                     "nodeMappings": nodeMaps, "relationshipMappings": relMaps},
      "configurations": {"idsToIgnore": []}}}

if __name__ == "__main__":
    m = build(sys.argv[1]); json.dump(m, open(sys.argv[2], "w"), indent=2)
    gs = m["dataModel"]["graphSchemaRepresentation"]["graphSchema"]
    print(len(gs["nodeLabels"]), "labels,", len(gs["relationshipTypes"]), "rel types,", len(gs["constraints"]), "constraints,", len(gs["indexes"]), "indexes")
