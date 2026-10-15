"""
Pre-flight validator. Run BEFORE uploading to the Aura console:
    python3 -I validate.py <csv_dir>
Part 1  schema rules derived from spec.py (what the importer / constraints would reject)
Part 2  business invariants (what makes the data believable as a GxP manufacturing record)
Exit code 1 if any rule fails.
"""
import csv, os, sys, re, datetime as dt
from collections import defaultdict, Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import spec

ASOF = dt.datetime(2026, 10, 13, 9, 0, 0)
FAILS = defaultdict(list); RULES = []
def rule(name):
    RULES.append(name); return name
def bad(name, msg):
    FAILS[name].append(msg)
def check(name, cond, msg):
    if not cond: bad(name, msg)

def P(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") if s else None
def Fl(s): return float(s) if s != "" else None

def load(d):
    T, R = {}, {}
    for label, n in spec.NODES.items():
        path = os.path.join(d, n["file"])
        rule_ = rule("S1 file present + header matches spec")
        if not os.path.exists(path): bad(rule_, f"missing {n['file']}"); T[label] = {}; continue
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f); exp = [p[0] for p in n["props"]]
            check(rule_, rd.fieldnames == exp, f"{n['file']} header {rd.fieldnames} != {exp}")
            rows = list(rd)
        T[label] = rows
    for r in spec.RELS:
        path = os.path.join(d, r["file"]); fc, tc = spec.rel_cols(r)
        if not os.path.exists(path): bad("S1 file present + header matches spec", f"missing {r['file']}"); R[r["type"]] = []; continue
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.DictReader(f); exp = [fc, tc] + [p[0] for p in r["props"]]
            check("S1 file present + header matches spec", rd.fieldnames == exp, f"{r['file']} header {rd.fieldnames} != {exp}")
            R[r["type"]] = list(rd)
    return T, R

def schema(T, R):
    K = {}
    for label, n in spec.NODES.items():
        key = n["key"]; rows = T[label]
        n1 = rule("S2 key present and unique"); n2 = rule("S3 unique natural props unique"); n3 = rule("S4 required props non-empty")
        n4 = rule("S5 value types parse"); n6 = rule("S6 enum values valid"); n7 = rule("S7 no surrounding whitespace / non-ASCII")
        seen = Counter(r[key] for r in rows)
        for k, c in seen.items():
            check(n1, k != "" and c == 1, f"{label}.{key}={k!r} appears {c}x")
        K[label] = set(seen)
        for up in n.get("unique", []):
            for k, c in Counter(r[up] for r in rows).items(): check(n2, c == 1 and k != "", f"{label}.{up}={k!r} appears {c}x")
        for r in rows:
            for pn, ty, req in n["props"]:
                v = r[pn]
                if req: check(n3, v != "", f"{label}[{r[key]}].{pn} empty")
                if v == "": continue
                try:
                    if ty == "integer": int(v)
                    elif ty == "float": float(v)
                    elif ty == "datetime": P(v)
                except Exception: bad(n4, f"{label}[{r[key]}].{pn}={v!r} is not {ty}")
                check(n7, v == v.strip() and v.isascii(), f"{label}[{r[key]}].{pn}={v!r}")
                if (label, pn) in spec.ENUMS: check(n6, v in spec.ENUMS[(label, pn)], f"{label}[{r[key]}].{pn}={v!r}")
    for r in spec.RELS:
        fc, tc = spec.rel_cols(r); rows = R[r["type"]]
        a, b = rule("S8 relationship endpoints exist (no orphans)"), rule("S9 no duplicate relationships")
        c_ = rule("S4 required props non-empty")
        for row in rows:
            check(a, row[fc] in K[r["frm"]], f"{r['type']}: {fc}={row[fc]!r} not in {r['frm']}")
            check(a, row[tc] in K[r["to"]], f"{r['type']}: {tc}={row[tc]!r} not in {r['to']}")
            for pn, ty, req in r["props"]:
                if req: check(c_, row[pn] != "", f"{r['type']}[{row[fc]}->{row[tc]}].{pn} empty")
                if row[pn]:
                    try: (int if ty == "integer" else float if ty == "float" else P if ty == "datetime" else str)(row[pn])
                    except Exception: bad("S5 value types parse", f"{r['type']}.{pn}={row[pn]!r}")
        for pair, c in Counter((row[fc], row[tc]) for row in rows).items(): check(b, c == 1, f"{r['type']} {pair} x{c}")

def business(T, R):
    ix = {l: {row[spec.NODES[l]["key"]]: row for row in rows} for l, rows in T.items()}
    def out(rel, frm_key=True):    # key -> [other end keys]
        fc, tc = spec.rel_cols(next(r for r in spec.RELS if r["type"] == rel)); d = defaultdict(list)
        for row in R[rel]: d[row[fc if frm_key else tc]].append(row)
        return d
    fc_ = lambda rel: spec.rel_cols(next(r for r in spec.RELS if r["type"] == rel))
    def one(rel, frm_key=True):
        f, t = fc_(rel); d = {}
        for row in R[rel]:
            k, v = (row[f], row[t]) if frm_key else (row[t], row[f]); d.setdefault(k, []).append(v)
        return d
    # ---- specification sanity
    rS = rule("B1 specification limits consistent with limitType")
    for s in T["Specification"]:
        lo, hi, lt = Fl(s["lowerLimit"]), Fl(s["upperLimit"]), s["limitType"]
        ok = {"Range": lo is not None and hi is not None and lo < hi, "NMT": lo is None and hi is not None,
              "NLT": lo is not None and hi is None, "Report": lo is None and hi is None}[lt]
        check(rS, ok, f"{s['specId']} {lt} lo={lo} hi={hi}")
    sp_prod, sp_assay = {}, {}
    for r in R["APPLIES_TO"]: sp_prod.setdefault(r["specId"], []).append(r["productCode"])
    for r in R["MEASURED_BY"]: sp_assay.setdefault(r["specId"], []).append(r["methodId"])
    rS2 = rule("B1b each spec has exactly one product + one method")
    for s in ix["Specification"]: check(rS2, len(sp_prod.get(s, [])) == 1 and len(sp_assay.get(s, [])) == 1, s)
    # ---- batches
    prod_of = {k: v[0] for k, v in one("OF_PRODUCT").items()}
    br_of = {}; prod_run = {}
    for r in R["PRODUCES"]: br_of[r["batchNumber"]] = r["equipmentId"]; prod_run[r["batchNumber"]] = r
    rBR = rule("B2 each batch has exactly 1 product, 1 bioreactor run, 1 cell bank")
    wcb = one("INOCULATED_FROM")
    for b in ix["Batch"]:
        check(rBR, b in prod_of and b in br_of and len(wcb.get(b, [])) == 1, b)
    rOv = rule("B3 bioreactor runs do not overlap; scale matches vessel; working vol <= nominal")
    byBR = defaultdict(list)
    for b, r in prod_run.items(): byBR[r["equipmentId"]].append((P(r["startTime"]), P(r["endTime"]) or ASOF, b))
    for eq, lst in byBR.items():
        lst.sort()
        for (s1, e1, b1), (s2, e2, b2) in zip(lst, lst[1:]): check(rOv, e1 <= s2, f"{eq}: {b1} overlaps {b2}")
    for b, r in prod_run.items():
        nominal = int(ix["Bioreactor"][r["equipmentId"]]["nominalVolumeL"])
        check(rOv, int(ix["Batch"][b]["scaleL"]) == nominal, f"{b} scale {ix['Batch'][b]['scaleL']} vs vessel {nominal}")
        check(rOv, float(r["workingVolumeL"]) <= nominal, f"{b} working volume")
    rCB = rule("B4 cell bank lineage: WCB derived from MCB that expresses the batch's product; bank prepared before inoculation")
    der = {r["bankId"]: r["parentBankId"] for r in R["DERIVED_FROM"]}; expr = {r["bankId"]: r["productCode"] for r in R["EXPRESSES"]}
    for b, w in wcb.items():
        w = w[0]; cb = ix["CellBank"][w]
        check(rCB, cb["bankType"] == "WCB" and w in der and expr.get(der[w]) == prod_of[b], f"{b} <- {w}")
        check(rCB, P(cb["preparedDate"]) <= P(prod_run[b]["startTime"]), f"{b} inoculated before {w} prepared")
    # ---- protocols & steps
    steps_of = defaultdict(list)
    for r in R["INCLUDES"]: steps_of[r["protocolId"]].append(ix["PurificationStep"][r["stepId"]])
    nxt = {r["stepId"]: r["nextStepId"] for r in R["FOLLOWED_BY"]}
    rPr = rule("B5 protocol steps numbered 1..n, FOLLOWED_BY chain matches stepNumber, steps belong to one protocol")
    owner = Counter(r["stepId"] for r in R["INCLUDES"])
    for pid, st in steps_of.items():
        nums = sorted(int(s["stepNumber"]) for s in st); check(rPr, nums == list(range(1, len(st) + 1)), f"{pid} numbers {nums}")
        byn = {int(s["stepNumber"]): s["stepId"] for s in st}
        for i in range(1, len(st)): check(rPr, nxt.get(byn.get(i)) == byn.get(i + 1), f"{pid} chain broken at {i}")
        check(rPr, byn.get(len(st)) not in nxt, f"{pid} last step has successor")
    for s, c in owner.items(): check(rPr, c == 1, f"step {s} in {c} protocols")
    rPv = rule("B6 protocol versioning: status/supersededDate/SUPERSEDES consistent")
    sup = {r["protocolId"]: r["supersededProtocolId"] for r in R["SUPERSEDES"]}; superseded_by = {v: k for k, v in sup.items()}
    for pid, p in ix["PurificationProtocol"].items():
        check(rPv, (p["status"] == "Superseded") == (p["supersededDate"] != ""), pid)
        check(rPv, (pid in superseded_by) == (p["status"] == "Superseded"), pid)
        if pid in sup: check(rPv, P(p["effectiveDate"]) > P(ix["PurificationProtocol"][sup[pid]]["effectiveDate"]), pid)
        if pid in superseded_by: check(rPv, P(p["supersededDate"]) == P(ix["PurificationProtocol"][superseded_by[pid]]["effectiveDate"]), pid)
    # ---- executions
    exec_batch = {r["executionId"]: r["batchNumber"] for r in R["PART_OF"]}; exec_step = {r["executionId"]: r["stepId"] for r in R["OF_STEP"]}
    proto = {r["batchNumber"]: r for r in R["UNDERGOES"]}
    execs = defaultdict(list)
    for e, b in exec_batch.items(): execs[b].append(ix["StepExecution"][e])
    rEx = rule("B7 executions: right protocol, effective at start, contiguous from step 1, sequential in time, after harvest")
    rEx2 = rule("B8 execution status/fields: completed => end+yield+pool; in-progress only last")
    rYd = rule("B9 yields: overall = product of step yields; DS mass = harvest vol x titer x yield; plausible ranges")
    for b, lst in execs.items():
        pr = proto.get(b)
        if not pr: bad(rEx, f"{b} has executions but no UNDERGOES"); continue
        pid = pr["protocolId"]; P_ = ix["PurificationProtocol"][pid]
        lst.sort(key=lambda e: int(ix["PurificationStep"][exec_step[e["executionId"]]]["stepNumber"]))
        nums = [int(ix["PurificationStep"][exec_step[e["executionId"]]]["stepNumber"]) for e in lst]
        check(rEx, nums == list(range(1, len(nums) + 1)), f"{b} step numbers {nums}")
        check(rEx, all(owner_p == pid for owner_p in [next(r["protocolId"] for r in R["INCLUDES"] if r["stepId"] == exec_step[e["executionId"]]) for e in lst]), f"{b} executes steps of another protocol")
        s0 = P(lst[0]["startTime"]); check(rEx, P(P_["effectiveDate"]) <= s0 and (not P_["supersededDate"] or s0 < P(P_["supersededDate"])), f"{b} protocol {pid} not effective at {s0}")
        harvest = P(prod_run[b]["endTime"]); check(rEx, harvest is not None and s0 >= harvest, f"{b} first step before harvest")
        check(rEx, P(pr["startTime"]) == s0, f"{b} UNDERGOES.startTime != first execution")
        for e1, e2 in zip(lst, lst[1:]): check(rEx, e1["endTime"] != "" and P(e1["endTime"]) <= P(e2["startTime"]), f"{b} overlap {e1['executionId']}")
        for i, e in enumerate(lst):
            done = e["status"] == "Completed"
            check(rEx2, done == (e["endTime"] != "") and done == (e["stepYieldPct"] != "") and done == (e["poolVolumeL"] != ""), e["executionId"])
            if not done: check(rEx2, i == len(lst) - 1, f"{e['executionId']} in progress but not last")
            if done: check(rEx, P(e["endTime"]) > P(e["startTime"]), e["executionId"]); check(rYd, 0 < float(e["stepYieldPct"]) <= 100, e["executionId"])
        nsteps = len(steps_of[pid]); full = len(lst) == nsteps and lst[-1]["status"] == "Completed"
        B = ix["Batch"][b]
        check(rEx2, (pr["endTime"] != "") == full, f"{b} UNDERGOES.endTime vs completion")
        check(rYd, (B["drugSubstanceG"] != "") == full and (B["overallYieldPct"] != "") == full, f"{b} DS fields vs completion")
        if full:
            ov = 1.0
            for e in lst: ov *= float(e["stepYieldPct"]) / 100
            check(rYd, abs(ov * 100 - float(B["overallYieldPct"])) <= 0.15, f"{b} overall {B['overallYieldPct']} vs {ov*100:.2f}")
            ds = float(B["harvestVolumeL"]) * float(B["titerGPerL"]) * float(B["overallYieldPct"]) / 100
            check(rYd, abs(ds - float(B["drugSubstanceG"])) <= 0.2, f"{b} DS g {B['drugSubstanceG']} vs {ds:.2f}")
            check(rYd, 40 <= float(B["overallYieldPct"]) <= 95, f"{b} yield {B['overallYieldPct']}")
        if B["harvestVolumeL"]:
            check(rYd, float(B["harvestVolumeL"]) <= int(B["scaleL"]) and 0.5 <= float(B["titerGPerL"]) <= 15, f"{b} harvest vol/titer")
    for b, B in ix["Batch"].items():
        check(rEx, (b in execs) or prod_run[b]["endTime"] == "" or B["status"] == "In Purification", f"{b} harvested but no executions and status {B['status']}")
        if B["status"] == "In Culture": check(rEx, prod_run[b]["endTime"] == "" and b not in execs, b)
    # ---- samples
    smp_batch = {r["sampleId"]: r["batchNumber"] for r in R["TAKEN_FROM"]}; smp_exec = {r["sampleId"]: r["executionId"] for r in R["TAKEN_AT"]}
    rSm = rule("B10 samples: taken at an execution of the same batch, at its end time")
    for s, row in ix["Sample"].items():
        e = smp_exec.get(s); check(rSm, e is not None and exec_batch.get(e) == smp_batch.get(s), s)
        if e: check(rSm, ix["StepExecution"][e]["endTime"] == row["collectedAt"], f"{s} collectedAt != execution end")
    # ---- test results
    res_spec = {r["resultId"]: r["specId"] for r in R["AGAINST_SPEC"]}; res_smp = {r["resultId"]: r["sampleId"] for r in R["ON_SAMPLE"]}
    res_assay = {r["resultId"]: r["methodId"] for r in R["USES_METHOD"]}; res_lab = {r["resultId"]: r["labId"] for r in R["CONDUCTED_IN"]}
    res_perf = {r["resultId"]: r["employeeId"] for r in R["PERFORMED_BY"]}; res_rev = {r["resultId"]: r["employeeId"] for r in R["REVIEWED_BY"]}
    res_inst = defaultdict(list)
    for r in R["USED_FOR"]: res_inst[r["resultId"]].append(r["instrumentId"])
    works = defaultdict(set)
    for r in R["WORKS_IN"]: works[r["employeeId"]].add(r["labId"])
    rO = rule("B11 outcome recomputes from value vs specification limits")
    rT = rule("B12 chain of custody: sample <= tested <= reviewed; reviewer != performer; roles + lab membership")
    rM = rule("B13 result links coherent: spec belongs to batch's product, sample point, method; instrument type/lab")
    for rid, t in ix["TestResult"].items():
        s = ix["Specification"][res_spec[rid]]; v = Fl(t["value"]); q = t["qualifier"]; lo, hi = Fl(s["lowerLimit"]), Fl(s["upperLimit"])
        exp = "Reported" if s["limitType"] == "Report" else ("OOS" if (lo is not None and v < lo) or (hi is not None and v > hi) else "Conforms")
        check(rO, t["outcome"] == exp, f"{rid} outcome {t['outcome']} but {q}{v} vs [{lo},{hi}] => {exp}")
        check(rO, t["unit"] == s["unit"], f"{rid} unit {t['unit']} vs spec {s['unit']}")
        sm = ix["Sample"][res_smp[rid]]; check(rT, P(t["testedAt"]) >= P(sm["collectedAt"]), f"{rid} tested before collected")
        check(rT, P(t["testedAt"]) <= ASOF, f"{rid} tested in the future")
        check(rT, (t["reviewStatus"] == "Reviewed") == (t["reviewedAt"] != "") == (rid in res_rev), f"{rid} review fields inconsistent")
        if rid in res_rev:
            check(rT, P(t["reviewedAt"]) > P(t["testedAt"]) and P(t["reviewedAt"]) <= ASOF, f"{rid} reviewedAt")
            check(rT, res_rev[rid] != res_perf[rid], f"{rid} reviewed by performer")
            check(rT, ix["Employee"][res_rev[rid]]["role"] == "QC Reviewer" and res_lab[rid] in works[res_rev[rid]], f"{rid} reviewer role/lab")
        check(rT, ix["Employee"][res_perf[rid]]["role"] == "QC Analyst" and res_lab[rid] in works[res_perf[rid]], f"{rid} analyst role/lab")
        b = smp_batch[sm["sampleId"]]
        check(rM, sp_prod[s["specId"]][0] == prod_of[b], f"{rid} spec {s['specId']} not for {b}'s product")
        check(rM, s["samplePoint"] == sm["samplePoint"], f"{rid} sample point {sm['samplePoint']} vs spec {s['samplePoint']}")
        check(rM, sp_assay[s["specId"]][0] == res_assay[rid], f"{rid} method differs from spec method")
        at = ix["Assay"][res_assay[rid]]["instrumentType"]; ins = [ix["Instrument"][i] for i in res_inst.get(rid, [])]
        check(rM, all(i["instrumentType"] in (at, "Liquid Handler") for i in ins) and (at == "" or any(i["instrumentType"] == at for i in ins)) and (at != "" or not ins), f"{rid} instrument types {[i['instrumentType'] for i in ins]} vs method {at!r}")
        loc = {r["instrumentId"]: r["labId"] for r in R["LOCATED_IN"]}
        check(rM, all(loc[i["instrumentId"]] == res_lab[rid] for i in ins), f"{rid} instrument not in conducting lab")
    rRt = rule("B14 retests: invalidated OOS has retest with attempt+1 on same sample/spec; only invalidated results are retested")
    retest = {r["resultId"]: r["originalResultId"] for r in R["RETEST_OF"]}
    for rid, o in retest.items():
        a, b = ix["TestResult"][rid], ix["TestResult"][o]
        check(rRt, b["resultStatus"] == "Invalidated" and b["outcome"] == "OOS" and int(a["attempt"]) == int(b["attempt"]) + 1 and res_smp[rid] == res_smp[o] and res_spec[rid] == res_spec[o], f"{rid}->{o}")
    # ---- deviations / disposition
    dev_batch = {r["deviationId"]: r["batchNumber"] for r in R["AFFECTS"]}; dev_trig = defaultdict(list)
    for r in R["TRIGGERED_BY"]: dev_trig[r["deviationId"]].append(r["resultId"])
    dev_exec = {r["deviationId"]: r["executionId"] for r in R["OCCURRED_AT"]}; dev_own = {r["deviationId"]: r["employeeId"] for r in R["OWNED_BY"]}
    rD = rule("B15 deviations: open<->no closedDate, closed has root cause, Major+ closed has CAPA, OOS linked to OOS result in same batch, owner is QA")
    open_dev = defaultdict(list); closed_dev = defaultdict(list)
    for d, row in ix["Deviation"].items():
        b = dev_batch.get(d); check(rD, b is not None, f"{d} affects no batch")
        check(rD, (row["status"] == "Open") == (row["closedDate"] == ""), d)
        if row["status"] == "Closed":
            check(rD, row["rootCause"] != "" and P(row["closedDate"]) >= P(row["openedDate"]) and P(row["closedDate"]) <= ASOF, d)
            if row["severity"] in ("Major", "Critical"): check(rD, row["capaNumber"] != "", f"{d} closed {row['severity']} without CAPA")
            closed_dev[b].append(row)
        else: open_dev[b].append(row)
        check(rD, ix["Employee"][dev_own[d]]["role"] == "QA Reviewer", d)
        if row["deviationType"] == "OOS Investigation":
            tr = dev_trig.get(d, []); check(rD, len(tr) == 1 and ix["TestResult"][tr[0]]["outcome"] == "OOS" and smp_batch[res_smp[tr[0]]] == b, f"{d} trigger")
            if tr: check(rD, P(row["openedDate"]) >= P(ix["TestResult"][tr[0]]["testedAt"]).replace(hour=0, minute=0, second=0), f"{d} opened before result")
        if d in dev_exec: check(rD, exec_batch[dev_exec[d]] == b, f"{d} occurred_at other batch")
    rQ = rule("B16 batch disposition rules (Released/Rejected/Pending QA/Under Investigation) hold")
    resp = defaultdict(list)
    for r in R["RESPONSIBLE_FOR"]: resp[r["batchNumber"]].append(r)
    res_by_batch = defaultdict(list)
    for rid in ix["TestResult"]: res_by_batch[smp_batch[res_smp[rid]]].append(ix["TestResult"][rid])
    for b, B in ix["Batch"].items():
        st = B["status"]; rel_specs = [s for s in ix["Specification"].values() if sp_prod[s["specId"]][0] == prod_of[b] and s["stage"] == "Release"]
        rel = [t for t in res_by_batch[b] if ix["Specification"][res_spec[t["resultId"]]]["stage"] == "Release"]
        valid = [t for t in rel if t["resultStatus"] == "Valid"]; have = {res_spec[t["resultId"]] for t in valid}
        complete = all(s["specId"] in have for s in rel_specs) and all(t["reviewStatus"] == "Reviewed" for t in valid)
        qa = [r for r in resp[b] if r["role"] == "QA Approver"]
        if st in ("Released", "Rejected"):
            check(rQ, B["dispositionDate"] != "" and len(qa) == 1 and not open_dev[b] and complete, f"{b} {st}: disp={B['dispositionDate']!r} qa={len(qa)} open={len(open_dev[b])} complete={complete}")
            lastev = max([P(t["reviewedAt"]) for t in rel if t["reviewedAt"]] + [P(d["closedDate"]) for d in closed_dev[b]])
            check(rQ, B["dispositionDate"] != "" and P(B["dispositionDate"]) >= lastev.replace(hour=0, minute=0, second=0) and P(B["dispositionDate"]) <= ASOF, f"{b} disposition before last review/closure")
            oos = any(t["outcome"] == "OOS" for t in valid)
            check(rQ, oos == (st == "Rejected"), f"{b} {st} but valid OOS={oos}")
        else:
            check(rQ, B["dispositionDate"] == "" and not qa, f"{b} {st} has disposition")
        if st == "Pending QA Review": check(rQ, complete and not open_dev[b], b)
        if st == "Under Investigation": check(rQ, bool(open_dev[b]), f"{b} under investigation without open deviation")
        if open_dev[b]: check(rQ, st in ("Under Investigation", "In Purification"), f"{b} open deviation but {st}")
        for r in resp[b]:
            want = {"Upstream Lead": "Upstream Operator", "Downstream Lead": "Downstream Operator", "Process Owner": "Process Scientist", "QA Approver": "QA Reviewer"}[r["role"]] if r["role"] in ("Upstream Lead", "Downstream Lead", "Process Owner", "QA Approver") else None
            check(rQ, want is not None and ix["Employee"][r["employeeId"]]["role"] == want, f"{b} {r['role']} held by {ix['Employee'][r['employeeId']]['role']}")
    rXe = rule("B17 step executed by downstream operators")
    for r in R["EXECUTED_BY"]: check(rXe, ix["Employee"][r["employeeId"]]["role"] == "Downstream Operator", r["executionId"])
    # ---- materials
    rMl = rule("B18 consumed material lots: approved, received before and not expired at use; one lot per material per batch; required materials present")
    lot_mat = {r["lotNumber"]: r["materialId"] for r in R["LOT_OF"]}
    req = defaultdict(list)
    for r in R["REQUIRES"]: req[r["stepId"]].append(r["materialId"])
    cons = defaultdict(list)
    for r in R["CONSUMED"]: cons[r["batchNumber"]].append(r)
    for b, rows in cons.items():
        mats = Counter(lot_mat[r["lotNumber"]] for r in rows)
        for m, c in mats.items(): check(rMl, c == 1, f"{b} consumed {c} lots of {m}")
        use = {}
        for m in ("MAT-001", "MAT-002", "MAT-003"): use[m] = P(prod_run[b]["startTime"])
        for e in execs.get(b, []):
            for m in req[exec_step[e["executionId"]]]: use[m] = P(e["startTime"])
        for r in rows:
            m = lot_mat[r["lotNumber"]]; lot = ix["MaterialLot"][r["lotNumber"]]
            check(rMl, m in use, f"{b} consumed {m} which no executed step requires")
            if m in use:
                check(rMl, lot["status"] in ("Approved", "Supplier Notification"), f"{b} used {lot['status']} lot {lot['lotNumber']}")
                check(rMl, P(lot["receivedDate"]) <= use[m] <= P(lot["expiryDate"]), f"{b} lot {lot['lotNumber']} not valid at {use[m]}")
        for m in use: check(rMl, m in mats, f"{b} missing consumption of {m}")
    # ---- reference data
    rE = rule("B19 reference data: instruments' types exist for every method; every method type has an instrument in the lab")
    for a in ix["Assay"].values():
        if a["instrumentType"]: check(rE, any(i["instrumentType"] == a["instrumentType"] for i in ix["Instrument"].values()), a["methodId"])
    rEm = rule("B20 employees: role allowed by lab membership (analysts/reviewers in exactly 1 lab, others none)")
    for e in ix["Employee"].values():
        n = len(works[e["employeeId"]]); check(rEm, n == (1 if e["role"] in ("QC Analyst", "QC Reviewer") else 0), f"{e['employeeId']} {e['role']} in {n} labs")

def main(d):
    T, R = load(d); schema(T, R)
    if FAILS:
        RULES.append("B* business invariants")
        bad("B* business invariants", "skipped: fix the schema errors above first (the business rules assume unique keys and valid foreign keys)")
    else:
        try: business(T, R)
        except Exception as ex:   # a crash is a failure, never a pass
            RULES.append("B* business invariants"); bad("B* business invariants", f"validator crashed: {ex!r}")
    names = list(dict.fromkeys(RULES)); fails = 0
    for n in names:
        f = FAILS.get(n, []); fails += bool(f)
        print(("FAIL " if f else "ok   ") + n + (f"  ({len(f)})" if f else ""))
        for m in f[:5]: print("       -", m)
    counts = sum(len(v) for v in T.values()), sum(len(v) for v in R.values())
    print(f"\n{counts[0]} nodes, {counts[1]} relationships checked; {fails} rule(s) failed")
    return 1 if fails else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
