"""
Generates a coherent synthetic biologics (CHO / mAb) drug-substance manufacturing data set.
Writes the CSVs defined in spec.py.  Deterministic (fixed seed).

Usage: python3 -I generate.py <out_dir>
"""
import csv, os, sys, math, random, datetime as dt
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import spec

rng = random.Random(20261013)
NOW = dt.datetime(2026, 10, 13, 9, 0, 0)          # data "as of" date
H, DAY = dt.timedelta(hours=1), dt.timedelta(days=1)

def ts(d):  return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else ""
def dts(d): return d.strftime("%Y-%m-%dT00:00:00Z") if d else ""
def U(a, b): return rng.uniform(a, b)
def clip(x, a, b): return max(a, min(b, x))
def N(m, s, a=-1e18, b=1e18): return clip(rng.gauss(m, s), a, b)
def LN(median, sigma, a, b): return clip(median * math.exp(rng.gauss(0, sigma)), a, b)
def rd(x, n): return round(x + 0.0, n)

NODES = defaultdict(list)       # label -> [dict]
RELS = defaultdict(list)        # rel type -> [dict]
def addn(label, **p):
    NODES[label].append(p); return p
def addr(t, a, b, **p):
    RELS[t].append(dict(_a=a, _b=b, **p))

# --------------------------------------------------------------------------- labs / people
LABS = [
 ("QC-BIOCHEM", "QC Biochemistry",       "QC",  "Bldg 2 Rm 210", "GMP QC"),
 ("QC-MICRO",   "QC Microbiology",       "QC",  "Bldg 2 Rm 118", "GMP QC"),
 ("QC-MOLBIO",  "QC Molecular Biology",  "QC",  "Bldg 2 Rm 140", "GMP QC"),
 ("AD-ANALYTIC","Analytical Development","AD",  "Bldg 4 Rm 305", "Non-GMP Development"),
]
for lid, name, dept, bld, scope in LABS:
    addn("Lab", labId=lid, name=name, department=dept, building=bld, gxpScope=scope)

FIRST = ["Maria","James","Priya","Wei","Samuel","Elena","Omar","Hannah","Diego","Aisha","Thomas","Yuki","Rachel","Kwame",
         "Sofia","Daniel","Nadia","Peter","Grace","Lucas","Mei","Andre","Olivia","Ravi","Claire","Tomas","Fatima","Ethan"]
LAST  = ["Alvarez","Becker","Chen","Dubois","Okafor","Novak","Patel","Lindqvist","Moreau","Tanaka","Rossi","Haddad","Kowalski",
         "Nguyen","Fischer","Ibrahim","Murphy","Santos","Petrov","Walsh","Yamamoto","Cohen","Barros","Singh","Larsen","Mensah"]
random_names = [(f, l) for f in FIRST for l in LAST]; rng.shuffle(random_names)
EMP = []     # dicts
def hire(role, dept, lab=None, n=1):
    for _ in range(n):
        f, l = random_names.pop()
        e = addn("Employee", employeeId=f"E{1001 + len(EMP)}", name=f"{f} {l}",
                 email=f"{f}.{l}@meridianbio.example".lower(), role=role, department=dept)
        e["_lab"] = lab; EMP.append(e)
        if lab: addr("WORKS_IN", e["employeeId"], lab)
hire("Upstream Operator", "Upstream Manufacturing", n=4)
hire("Downstream Operator", "Downstream Manufacturing", n=5)
hire("Process Scientist", "MS&T", n=3)
hire("QA Reviewer", "Quality Assurance", n=2)
for lid, an, rv in [("QC-BIOCHEM", 4, 2), ("QC-MICRO", 2, 1), ("QC-MOLBIO", 1, 1), ("AD-ANALYTIC", 2, 1)]:
    dept = next(l[1] for l in LABS if l[0] == lid)
    hire("QC Analyst", dept, lid, an); hire("QC Reviewer", dept, lid, rv)
def emps(role, lab=None): return [e for e in EMP if e["role"] == role and (lab is None or e["_lab"] == lab)]

# --------------------------------------------------------------------------- instruments
INSTR = []
def instr(lab, itype, abbr, name, mfr, model):
    n = sum(1 for i in INSTR if i["_lab"] == lab and i["instrumentType"] == itype) + 1
    last = NOW - dt.timedelta(days=rng.randint(10, 150))
    i = addn("Instrument", instrumentId=f"INS-{lab}-{abbr}-{n:02d}", name=f"{name} {n}", instrumentType=itype,
             manufacturer=mfr, model=model, status="In Service", lastCalibrated=dts(last), calibrationDue=dts(last + dt.timedelta(days=180)))
    i["_lab"] = lab; INSTR.append(i); addr("LOCATED_IN", i["instrumentId"], lab)
for lab, spec_ in {
  "AD-ANALYTIC": [("Plate Reader","PR","Plate Reader","Agilent BioTek","Synergy H1"), ("HPLC","HPLC","HPLC","Agilent","1260 Infinity II"),
                  ("Capillary Electrophoresis","CE","cIEF Analyzer","ProteinSimple","Maurice"), ("UV-Vis","UV","Variable Pathlength UV","C Technologies","SoloVPE"),
                  ("Liquid Handler","LH","Liquid Handler","Hamilton","Microlab STAR"), ("pH Meter","PH","pH Meter","Mettler Toledo","SevenExcellence")],
  "QC-BIOCHEM":  [("Plate Reader","PR","Plate Reader","Molecular Devices","SpectraMax iD5"), ("Plate Reader","PR","Plate Reader","BMG Labtech","CLARIOstar Plus"),
                  ("HPLC","HPLC","HPLC","Agilent","1290 Infinity II"), ("HPLC","HPLC","HPLC","Waters","Alliance iS"),
                  ("Capillary Electrophoresis","CE","cIEF Analyzer","ProteinSimple","Maurice"), ("UV-Vis","UV","Variable Pathlength UV","C Technologies","SoloVPE"),
                  ("Liquid Handler","LH","Liquid Handler","Tecan","Fluent 780"), ("Liquid Handler","LH","Liquid Handler","Hamilton","Microlab STAR"),
                  ("pH Meter","PH","pH Meter","Mettler Toledo","SevenExcellence")],
  "QC-MICRO":    [("Plate Reader","PR","Kinetic Plate Reader","Agilent BioTek","Synergy HTX")],
  "QC-MOLBIO":   [("qPCR","QPCR","qPCR System","Thermo Fisher Scientific","QuantStudio 7 Flex")],
}.items():
    for t in spec_: instr(lab, *t)

# --------------------------------------------------------------------------- assays
ASSAYS = {  # methodId: (name, technique, instrumentType, aux instrument types, lab dept)
 "AM-TITER-001": ("Titer by Protein A HPLC",            "HPLC",              "HPLC",                      [], "BIOCHEM"),
 "AM-SEC-001":   ("Purity by SEC-HPLC",                 "HPLC",              "HPLC",                      [], "BIOCHEM"),
 "AM-CIEF-001":  ("Charge Variants by cIEF",            "Capillary IEF",     "Capillary Electrophoresis", [], "BIOCHEM"),
 "AM-HCP-001":   ("Host Cell Protein ELISA",            "ELISA",             "Plate Reader",              ["Liquid Handler"], "BIOCHEM"),
 "AM-PRA-001":   ("Residual Protein A ELISA",           "ELISA",             "Plate Reader",              ["Liquid Handler"], "BIOCHEM"),
 "AM-A280-001":  ("Protein Concentration by A280",      "UV-Vis",            "UV-Vis",                    [], "BIOCHEM"),
 "AM-PH-001":    ("pH by Potentiometry",                "Potentiometry",     "pH Meter",                  [], "BIOCHEM"),
 "AM-ENDO-001":  ("Endotoxin by Kinetic Chromogenic LAL","Kinetic LAL",      "Plate Reader",              [], "MICRO"),
 "AM-BIOB-001":  ("Bioburden by Membrane Filtration",   "Membrane filtration", None,                      [], "MICRO"),
 "AM-DNA-001":   ("Residual Host Cell DNA by qPCR",     "qPCR",              "qPCR",                      [], "MOLBIO"),
}
for mid, (name, tech, it, aux, _) in ASSAYS.items():
    addn("Assay", methodId=mid, name=name, technique=tech, version=f"{rng.choice([2,3,4])}.0", status="Validated",
         instrumentType=it or "", description=f"{name}. Validated per ICH Q2(R2); executed under GMP controls.")
LAB_BY_DEPT = {"BIOCHEM": "QC-BIOCHEM", "MICRO": "QC-MICRO", "MOLBIO": "QC-MOLBIO"}

# --------------------------------------------------------------------------- products, cell banks
PRODUCTS = [
 dict(code="BTX-101", modality="Monoclonal antibody", target="IL-23 p19", iso="IgG1", mw=148.5, phase="Phase 3", cl="CHO-K1 GS-KO",
      conc=100, ctol=10, ph=5.8, ptol=0.3, titer=5.2, hmw=2.0, mono=97.0, main=60.0, acidic=35.0, doc=101, bisp=False,
      form="20 mM histidine, 8% sucrose, 0.04% polysorbate 80, pH 5.8", scales=[500,2000,2000,500,2000,2000,2000,2000], first=(2024,3,1)),
 dict(code="BTX-202", modality="Monoclonal antibody", target="PD-1", iso="IgG4", mw=146.2, phase="Phase 2", cl="CHO-DG44",
      conc=25, ctol=2.5, ph=5.5, ptol=0.3, titer=3.8, hmw=2.0, mono=97.0, main=55.0, acidic=35.0, doc=202, bisp=False,
      form="25 mM acetate, 9% sucrose, 0.02% polysorbate 80, pH 5.5", scales=[200,500,500,200,500,500], first=(2024,6,1)),
 dict(code="BTX-303", modality="Bispecific antibody", target="CD3 x BCMA", iso="IgG1 (knob-into-hole)", mw=146.8, phase="Phase 1", cl="CHO-K1 GS-KO",
      conc=20, ctol=2.0, ph=6.0, ptol=0.3, titer=2.4, hmw=3.0, mono=95.0, main=50.0, acidic=40.0, doc=303, bisp=True,
      form="20 mM histidine, 6% trehalose, 0.02% polysorbate 20, pH 6.0", scales=[50,50,50,200], first=(2025,8,1)),
 dict(code="BTX-404", modality="Fc-fusion protein", target="TNF-alpha", iso="IgG1 Fc", mw=92.4, phase="Phase 2", cl="CHO-S",
      conc=50, ctol=5, ph=6.5, ptol=0.3, titer=3.1, hmw=3.0, mono=96.0, main=55.0, acidic=40.0, doc=404, bisp=False,
      form="10 mM phosphate, 140 mM NaCl, pH 6.5", scales=[200,200,500,500,200], first=(2024,9,1)),
 dict(code="BTX-505", modality="Monoclonal antibody", target="TSLP", iso="IgG1", mw=148.1, phase="Phase 3", cl="CHO-K1 GS-KO",
      conc=150, ctol=15, ph=5.5, ptol=0.3, titer=6.1, hmw=2.0, mono=97.0, main=60.0, acidic=35.0, doc=505, bisp=False,
      form="20 mM histidine, 5% proline, 0.03% polysorbate 80, pH 5.5", scales=[500,2000,2000,2000,500,2000,2000], first=(2025,1,1)),
]
for p in PRODUCTS:
    addn("Product", productCode=p["code"], modality=p["modality"], targetAntigen=p["target"], isotype=p["iso"],
         molecularWeightKDa=p["mw"], developmentPhase=p["phase"], formulation=p["form"])
    mcb = f"MCB-{p['code'].replace('-','')}"
    addn("CellBank", bankId=mcb, bankType="MCB", cellLine=p["cl"], passageNumber=rng.randint(12, 18), vialCount=rng.randint(180, 240),
         preparedDate=dts(dt.datetime(2022, rng.randint(1, 12), rng.randint(1, 28))), status="Active")
    addr("EXPRESSES", mcb, p["code"])
    p["wcbs"] = []
    for k in range(2 if p["code"] == "BTX-101" else 1):
        prep = dt.datetime(2023, 9, 15) if k == 0 else dt.datetime(2025, 10, 6)
        wid = f"WCB-{p['code'].replace('-','')}-{k+1:02d}"
        addn("CellBank", bankId=wid, bankType="WCB", cellLine=p["cl"], passageNumber=rng.randint(20, 26), vialCount=rng.randint(80, 120),
             preparedDate=dts(prep), status="Active")
        addr("DERIVED_FROM", wid, mcb); p["wcbs"].append((prep, wid))

# --------------------------------------------------------------------------- materials & lots
MATS = [  # id, name, category, supplier, grade
 ("MAT-001","CHO Production Basal Medium","Media","Thermo Fisher Scientific","cGMP"),
 ("MAT-002","CHO Feed Medium","Media","Thermo Fisher Scientific","cGMP"),
 ("MAT-003","Antifoam C Emulsion","Additive","MilliporeSigma","cGMP"),
 ("MAT-010","Depth Filter (Millistak+ HC)","Filter","MilliporeSigma","cGMP"),
 ("MAT-011","Protein A Resin (MabSelect SuRe)","Resin","Cytiva","cGMP"),
 ("MAT-012","Cation Exchange Resin (Capto S ImpAct)","Resin","Cytiva","cGMP"),
 ("MAT-013","Anion Exchange Resin (Capto Q)","Resin","Cytiva","cGMP"),
 ("MAT-014","HIC Resin (Capto Phenyl ImpRes)","Resin","Cytiva","cGMP"),
 ("MAT-015","Viral Filter (Viresolve Pro)","Filter","MilliporeSigma","cGMP"),
 ("MAT-016","UF/DF Cassette 30 kDa (Pellicon 3)","Filter","MilliporeSigma","cGMP"),
 ("MAT-017","Sterile Filter 0.2 um (Sartopore 2 XLG)","Filter","Sartorius","cGMP"),
 ("MAT-018","Equilibration/Wash Buffer (Tris)","Buffer","In-house Buffer Prep","In-house"),
 ("MAT-019","Neutralization Buffer (Tris base)","Buffer","In-house Buffer Prep","In-house"),
 ("MAT-020","Formulation Buffer","Buffer","In-house Buffer Prep","In-house"),
]
SHELF = {"Media": (390, 540), "Additive": (730, 730), "Filter": (1095, 1095), "Resin": (730, 730), "Buffer": (180, 180)}
INTERVAL = {"Media": (130, 200), "Additive": (200, 260), "Filter": (200, 280), "Resin": (170, 230), "Buffer": (80, 100)}
LOTS = defaultdict(list)   # material -> [lot dicts]
SUPPLIER_NOTIFICATION_MAT = "MAT-011"
rejected_done = False
for mid, name, cat, sup, grade in MATS:
    addn("Material", materialId=mid, name=name, category=cat, supplier=sup, grade=grade)
    d = dt.datetime(2023, 9, 1) + dt.timedelta(days=rng.randint(0, 60)); n = 0
    while d < NOW:
        n += 1
        lot = addn("MaterialLot", lotNumber=f"L{d:%y}-{mid[-3:]}-{n:03d}",
                   supplierLotNumber=("" if sup.startswith("In-house") else f"{rng.choice('ABCDEFGH')}{rng.randint(10**6, 10**7-1)}"),
                   receivedDate=dts(d), expiryDate=dts(d + dt.timedelta(days=rng.randint(*SHELF[cat]))), status="Approved")
        lot["_recv"] = d; lot["_exp"] = d + dt.timedelta(days=int(0)) ; lot["_mat"] = mid
        lot["_exp"] = dt.datetime.strptime(lot["expiryDate"], "%Y-%m-%dT%H:%M:%SZ")
        addr("LOT_OF", lot["lotNumber"], mid); LOTS[mid].append(lot)
        d += dt.timedelta(days=rng.randint(*INTERVAL[cat]))
# special statuses
LOTS["MAT-001"][2]["status"] = "Rejected"; LOTS["MAT-001"][2]["_rejected"] = True            # failed incoming QC, never used
LOTS[SUPPLIER_NOTIFICATION_MAT][2]["status"] = "Supplier Notification"                      # supplier notified a resin issue after use
for mid in ("MAT-010", "MAT-017"):
    LOTS[mid][-1]["status"] = "Quarantine"                                                   # newest receipt awaiting QC release
LOTS["MAT-020"][-1]["status"] = "Quarantine"
def usable(lot, when): return lot["status"] in ("Approved", "Supplier Notification") and lot["_recv"] + 2*DAY <= when <= lot["_exp"]
def pick_lot(mid, when):
    ok = [l for l in LOTS[mid] if usable(l, when)]
    ok.sort(key=lambda l: l["_recv"])
    if not ok: raise RuntimeError(f"no valid lot for {mid} at {when}")
    return ok[-1] if (len(ok) == 1 or rng.random() < 0.7) else ok[-2]

# --------------------------------------------------------------------------- bioreactors
BR = [  # id, vendor, model, volume, room
 ("BR-050-01","Sartorius","Biostat STR 50",50,"PD Suite A"), ("BR-050-02","Sartorius","Biostat STR 50",50,"PD Suite A"),
 ("BR-200-01","Cytiva","Xcellerex XDR-200",200,"Clinical Suite 1"), ("BR-200-02","Cytiva","Xcellerex XDR-200",200,"Clinical Suite 1"),
 ("BR-500-01","Thermo Fisher Scientific","HyPerforma DynaDrive S.U.B. 500",500,"Clinical Suite 2"), ("BR-500-02","Thermo Fisher Scientific","HyPerforma DynaDrive S.U.B. 500",500,"Clinical Suite 2"),
 ("BR-2000-01","Sartorius","Biostat STR 2000",2000,"Commercial Suite 1"), ("BR-2000-02","Sartorius","Biostat STR 2000",2000,"Commercial Suite 1"),
 ("BR-2000-03","Cytiva","Xcellerex XDR-2000",2000,"Commercial Suite 2"),
]
BRS = []
for eid, mfr, model, vol, room in BR:
    b = addn("Bioreactor", equipmentId=eid, type="Single-use stirred tank", manufacturer=mfr, model=model, nominalVolumeL=vol,
             location=room, status="Qualified", qualifiedDate=dts(dt.datetime(2023, 6, 1) + dt.timedelta(days=rng.randint(0, 90))))
    b["_free"] = dt.datetime(2024, 1, 15); BRS.append(b)

# --------------------------------------------------------------------------- protocols
STEPS = [  # name, type, params(v1, v2), yield range, hours, materials required
 ("Harvest Clarification","Filtration","Depth filtration then 0.2 um; flux <= {flux} LMH",(96,99),8,["MAT-010"]),
 ("Protein A Affinity Capture","Chromatography","MabSelect SuRe; load <= {load} g/L resin; elution pH 3.6",(90,96),12,["MAT-011","MAT-018"]),
 ("Low pH Viral Inactivation","Viral Inactivation","pH 3.5 +/- 0.1; hold 60 +/- 5 min; neutralize to pH 5.5",(97,100),4,["MAT-019"]),
 ("Cation Exchange Chromatography","Chromatography","Capto S ImpAct bind-elute; load <= {cex} g/L; salt gradient elution",(85,95),12,["MAT-012"]),
 ("Hydrophobic Interaction Chromatography","Chromatography","Capto Phenyl ImpRes flow-through/weak partitioning; load <= 30 g/L",(80,92),10,["MAT-014"]),
 ("Anion Exchange Chromatography","Chromatography","Capto Q flow-through; load <= 200 g/L",(94,99),7,["MAT-013"]),
 ("Viral Filtration","Viral Filtration","20 nm nanofilter; <= 2.0 bar; pre/post-use integrity test",(96,99.5),10,["MAT-015"]),
 ("Ultrafiltration/Diafiltration","UF/DF","30 kDa cassette; {dv} diavolumes into formulation buffer",(94,99),16,["MAT-016","MAT-020"]),
 ("Final Filtration and Bulk Fill","Filtration","0.2 um sterile filtration; fill into single-use bags",(97,99.5),6,["MAT-017"]),
]
PARAMS = {1: dict(flux=100, load=30, cex=35, dv=8), 2: dict(flux=120, load=35, cex=40, dv=10)}
V2_DATE = dt.datetime(2025, 7, 1)
SAMPLE_STEP = {"Harvest Clarification": "Harvest (clarified)", "Protein A Affinity Capture": "Protein A Eluate Pool",
               "Cation Exchange Chromatography": "CEX Eluate Pool", "Ultrafiltration/Diafiltration": "UF/DF Retentate Pool",
               "Final Filtration and Bulk Fill": "Drug Substance"}
SP_STEP = {v: k for k, v in SAMPLE_STEP.items()}
for p in PRODUCTS:
    p["protos"] = []
    versions = [2] if p["code"] == "BTX-303" else [1, 2]
    if p["code"] == "BTX-303": versions = [1]
    for v in versions:
        doc = f"SOP-DSP-{p['doc']:04d}"; pid = f"{doc}-v{v}.0"
        eff = dt.datetime(2023, 11, 1) if v == 1 else V2_DATE
        if p["code"] == "BTX-303": eff = dt.datetime(2025, 6, 1)
        sup = V2_DATE if (v == 1 and len(versions) > 1) else None
        addn("PurificationProtocol", protocolId=pid, documentNumber=doc, name=f"{p['code']} Drug Substance Purification",
             version=f"{v}.0", status="Superseded" if sup else "Effective", effectiveDate=dts(eff), supersededDate=dts(sup),
             description=f"Downstream purification of {p['code']} ({p['modality']}) from clarified CHO harvest to bulk drug substance.")
        steps = [s for s in STEPS if p["bisp"] or s[0] != "Hydrophobic Interaction Chromatography"]
        prev = None; plist = []
        for i, (nm, ty, par, yr, hrs, mats) in enumerate(steps, 1):
            sid = f"{pid}-S{i:02d}"
            addn("PurificationStep", stepId=sid, stepNumber=i, stepName=nm, stepType=ty, operatingParameters=par.format(**PARAMS[v]))
            addr("INCLUDES", pid, sid)
            if prev: addr("FOLLOWED_BY", prev, sid)
            for m in mats: addr("REQUIRES", sid, m)
            prev = sid; plist.append(dict(stepId=sid, name=nm, number=i, yr=yr, hrs=hrs, mats=mats))
        p["protos"].append(dict(id=pid, eff=eff, sup=sup, steps=plist))
        if v == 2 and len(versions) > 1: addr("SUPERSEDES", pid, f"{doc}-v1.0")
def protocol_for(p, when):
    for pr in p["protos"]:
        if pr["eff"] <= when and (pr["sup"] is None or when < pr["sup"]): return pr
    return p["protos"][0]

# --------------------------------------------------------------------------- specifications
def spec_rows(p):
    c, ct, ph, pt = p["conc"], p["ctol"], p["ph"], p["ptol"]
    hm_cex = 4.0 if p["bisp"] else 3.0
    # key, attribute, category, stage, samplepoint, unit, limitType, lo, hi, assay
    return [
     ("TITER-H","Titer","Productivity","In-Process","Harvest (clarified)","g/L","Report",None,None,"AM-TITER-001"),
     ("BIOB-H","Bioburden","Safety","In-Process","Harvest (clarified)","CFU/10 mL","NMT",None,10,"AM-BIOB-001"),
     ("HCP-PA","Host Cell Protein","Process Impurity","In-Process","Protein A Eluate Pool","ng/mg","NMT",None,8000,"AM-HCP-001"),
     ("HMW-PA","High Molecular Weight Species","Product Impurity","In-Process","Protein A Eluate Pool","%","Report",None,None,"AM-SEC-001"),
     ("HCP-CEX","Host Cell Protein","Process Impurity","In-Process","CEX Eluate Pool","ng/mg","NMT",None,300,"AM-HCP-001"),
     ("HMW-CEX","High Molecular Weight Species","Product Impurity","In-Process","CEX Eluate Pool","%","NMT",None,hm_cex,"AM-SEC-001"),
     ("CONC-UF","Protein Concentration","General","In-Process","UF/DF Retentate Pool","mg/mL","Range",c-1.2*ct,c+1.2*ct,"AM-A280-001"),
     ("PH-UF","pH","General","In-Process","UF/DF Retentate Pool","pH units","Range",ph-pt-0.1,ph+pt+0.1,"AM-PH-001"),
     ("CONC-DS","Protein Concentration","General","Release","Drug Substance","mg/mL","Range",c-ct,c+ct,"AM-A280-001"),
     ("PH-DS","pH","General","Release","Drug Substance","pH units","Range",ph-pt,ph+pt,"AM-PH-001"),
     ("MONO-DS","Monomer (SEC-HPLC)","Purity","Release","Drug Substance","%","NLT",p["mono"],None,"AM-SEC-001"),
     ("HMW-DS","High Molecular Weight Species","Product Impurity","Release","Drug Substance","%","NMT",None,p["hmw"],"AM-SEC-001"),
     ("MAIN-DS","Main Isoform (cIEF)","Charge Variants","Release","Drug Substance","%","NLT",p["main"],None,"AM-CIEF-001"),
     ("ACID-DS","Acidic Variants (cIEF)","Charge Variants","Release","Drug Substance","%","NMT",None,p["acidic"],"AM-CIEF-001"),
     ("HCP-DS","Host Cell Protein","Process Impurity","Release","Drug Substance","ng/mg","NMT",None,100,"AM-HCP-001"),
     ("DNA-DS","Residual Host Cell DNA","Process Impurity","Release","Drug Substance","pg/mg","NMT",None,10,"AM-DNA-001"),
     ("PRA-DS","Residual Protein A","Process Impurity","Release","Drug Substance","ng/mg","NMT",None,10,"AM-PRA-001"),
     ("ENDO-DS","Endotoxin","Safety","Release","Drug Substance","EU/mg","NMT",None,0.5,"AM-ENDO-001"),
     ("BIOB-DS","Bioburden","Safety","Release","Drug Substance","CFU/10 mL","NMT",None,1,"AM-BIOB-001"),
    ]
for p in PRODUCTS:
    p["specs"] = {}
    for key, attr, cat, stage, sp, unit, lt, lo, hi, assay in spec_rows(p):
        sid = f"SPEC-{p['code'].replace('-','')}-{key}"
        s = addn("Specification", specId=sid, attribute=attr, category=cat, stage=stage, samplePoint=sp, unit=unit, limitType=lt,
                 lowerLimit=("" if lo is None else rd(lo, 2)), upperLimit=("" if hi is None else rd(hi, 2)))
        s["_key"] = key; s["_assay"] = assay; p["specs"][key] = s
        addr("APPLIES_TO", sid, p["code"]); addr("MEASURED_BY", sid, assay)

def gen_value(key, p):
    """-> (qualifier, value) for a conforming result."""
    c, ct, ph, pt = p["conc"], p["ctol"], p["ph"], p["ptol"]
    if key == "TITER-H":  return "=", rd(N(p["titer"], 0.35, 1.0, 12), 2)
    if key == "BIOB-H":   return "=", float(0 if rng.random() < 0.88 else rng.randint(1, 3))
    if key == "HCP-PA":   return "=", rd(LN(2200, .5, 400, 7000), 0)
    if key == "HMW-PA":   return "=", rd(N(2.4, .5, 1.2, 4.2), 2)
    if key == "HCP-CEX":  return "=", rd(LN(60, .5, 10, 250), 0)
    if key == "HMW-CEX":  return "=", rd(N(.9 + (1.0 if p["bisp"] else 0), .25, .4, 2.2), 2)
    if key == "CONC-UF":  return "=", rd(clip(N(c, .025*c), c-.9*ct, c+.9*ct), 1)
    if key == "PH-UF":    return "=", rd(clip(N(ph, .05), ph-.15, ph+.15), 2)
    if key == "CONC-DS":  return "=", rd(clip(N(c, .02*c), c-.75*ct, c+.75*ct), 1)
    if key == "PH-DS":    return "=", rd(clip(N(ph, .04), ph-.12, ph+.12), 2)
    if key == "MONO-DS":  return "=", rd(N(p["mono"]+1.8, .3, p["mono"]+.6, 99.7), 1)
    if key == "HMW-DS":   return "=", rd(N(p["hmw"]*.45, .2, .3, p["hmw"]-.4), 1)
    if key == "MAIN-DS":  return "=", rd(N(p["main"]+10, 3, p["main"]+3, 80), 1)
    if key == "ACID-DS":  return "=", rd(N(p["acidic"]-11, 3.5, 12, p["acidic"]-4), 1)
    if key == "HCP-DS":   return "=", rd(LN(12, .6, 2, 70), 0)
    if key == "DNA-DS":   return ("<", 1.0) if rng.random() < .85 else ("=", rd(N(2, .6, 1.0, 5), 1))
    if key == "PRA-DS":   return ("<", 1.0) if rng.random() < .85 else ("=", rd(N(2, .5, 1.0, 4), 1))
    if key == "ENDO-DS":  return ("<", 0.05) if rng.random() < .4 else ("=", rd(U(.05, .2), 2))
    if key == "BIOB-DS":  return ("<", 1.0) if rng.random() < .9 else ("=", 0.0)
    raise KeyError(key)
def gen_oos(s):
    if s["limitType"] == "NMT": return "=", rd(float(s["upperLimit"]) * U(1.1, 1.45), 2)
    return "=", rd(float(s["lowerLimit"]) - U(.8, 3.0), 1)
def outcome(s, q, v):
    if s["limitType"] == "Report": return "Reported"
    lo = None if s["lowerLimit"] == "" else float(s["lowerLimit"]); hi = None if s["upperLimit"] == "" else float(s["upperLimit"])
    if lo is not None and v < lo: return "OOS"
    if hi is not None and v > hi: return "OOS"
    return "Conforms"
TURN = {"AM-TITER-001": (.4, 2), "AM-SEC-001": (1, 5), "AM-CIEF-001": (2, 6), "AM-HCP-001": (3, 8), "AM-PRA-001": (3, 8),
        "AM-A280-001": (.3, 2), "AM-PH-001": (.2, 1.5), "AM-ENDO-001": (2, 6), "AM-BIOB-001": (6, 9), "AM-DNA-001": (4, 9)}

# --------------------------------------------------------------------------- batches
plan = []
for p in PRODUCTS:
    y, m, d0 = p["first"]; lo = dt.datetime(y, m, d0); hi = dt.datetime(2026, 8, 20)
    for sc in p["scales"]:
        plan.append((lo + dt.timedelta(days=rng.random() * (hi - lo).days), p, sc))
plan.sort(key=lambda t: t[0])
# force a realistic tail of in-flight work (culture, purification, QC testing, QA review, open investigation)
for off, k in zip([2, 11, 17, 21, 28, 36, 52], rng.sample(range(len(plan)), 7)):
    d_, p_, sc_ = plan[k]; plan[k] = (NOW - dt.timedelta(days=off), p_, sc_)
plan.sort(key=lambda t: t[0])
BATCHES = []
CULT = {50: (12, 14), 200: (13, 15), 500: (14, 15), 2000: (14, 16)}
for desired, p, sc in plan:
    pool = [b for b in BRS if b["nominalVolumeL"] == sc]
    b = min(pool, key=lambda x: max(x["_free"], desired))
    start = max(b["_free"], desired).replace(hour=rng.randint(7, 10), minute=rng.randint(0, 59), second=0, microsecond=0)
    if start > NOW - 2 * DAY: continue
    days = rng.randint(*CULT[sc]); harvest = start + dt.timedelta(days=days, hours=rng.randint(0, 5))
    b["_free"] = harvest + dt.timedelta(days=rng.randint(3, 6))
    BATCHES.append(dict(p=p, scale=sc, br=b, start=start, harvest=harvest))
BATCHES.sort(key=lambda x: x["start"])
seq = defaultdict(int)
for B in BATCHES:
    p = B["p"]; yy = B["start"].year % 100; seq[(p["code"], yy)] += 1
    B["num"] = f"{p['code'].replace('-','')}-{yy:02d}-{seq[(p['code'], yy)]:03d}"
    B["gmp"] = "Non-GMP" if (B["scale"] == 50 or (p["bisp"] and B["scale"] < 200)) else "GMP"

# ---- downstream execution timeline (no scenarios yet)
for B in BATCHES:
    p = B["p"]; B["steps"] = []; B["proto"] = None
    if B["harvest"] > NOW: continue
    pr = protocol_for(p, B["harvest"]); B["proto"] = pr
    t = B["harvest"] + dt.timedelta(hours=rng.randint(2, 8)); mass0 = None
    hv = rd(B["br"]["nominalVolumeL"] * U(.74, .84) * .97, 1); titer = rd(N(p["titer"], .35, 1.0, 12), 2)
    B["hv"], B["titer"] = hv, titer
    mass = hv * titer; yields = []
    conc_by_step = [titer, 18, 17, 14, 11, 10, 10, p["conc"], p["conc"]*.98]
    if p["bisp"]: conc_by_step = [titer, 18, 17, 14, 12, 11, 10, 10, p["conc"], p["conc"]*.98]
    for i, st in enumerate(pr["steps"]):
        dur = st["hrs"] * (1 + B["scale"] / 4000) * U(.85, 1.2)
        end = t + dt.timedelta(hours=dur)
        y = rd(U(*st["yr"]), 1); mass *= y / 100
        ex = dict(st=st, start=t, end=end, yield_=y, mass=mass, vol=rd(mass / conc_by_step[i], 1), num=B["num"])
        B["steps"].append(ex)
        t = end + dt.timedelta(hours=U(3, 30))
    B["overall"] = rd(math.prod(e["yield_"] for e in B["steps"]) / (100 ** (len(B["steps"]) - 1)), 1)
    B["ds_g"] = rd(hv * titer * B["overall"] / 100, 1)
    B["ds_end"] = B["steps"][-1]["end"]

# --------------------------------------------------------------------------- samples & results (planned, before scenarios)
for B in BATCHES:
    B["samples"] = {}; B["results"] = []
    for ex in B["steps"]:
        sp = SAMPLE_STEP.get(ex["st"]["name"])
        if not sp or ex["end"] > NOW: continue
        stage = "Release" if sp == "Drug Substance" else "In-Process"
        B["samples"][sp] = dict(sp=sp, type=stage, at=ex["end"], ex=ex)

def lab_for(assay, gmp):
    dept = ASSAYS[assay][4]
    if dept == "BIOCHEM" and gmp == "Non-GMP": return "AD-ANALYTIC"
    return LAB_BY_DEPT[dept]
def new_result(B, key, s_row, smp, attempt=1, force_oos=False, start_at=None):
    p = B["p"]; assay = s_row["_assay"]
    q, v = gen_oos(s_row) if force_oos else gen_value(key, p)
    out = outcome(s_row, q, v)
    lab = lab_for(assay, B["gmp"]); base = start_at or smp["at"]
    tested = base + dt.timedelta(days=U(*TURN[assay]) + (0 if smp["type"] == "In-Process" else 0.5))
    r = dict(B=B, key=key, spec=s_row, smp=smp, q=q, v=v, unit=s_row["unit"], out=out, status="Valid", attempt=attempt, tested=tested,
             lab=lab, assay=assay, reviewed=tested + dt.timedelta(days=U(1, 4)), orig=None)
    return r
for B in BATCHES:
    p = B["p"]
    for key, s_row in p["specs"].items():
        smp = B["samples"].get(s_row["samplePoint"])
        if not smp: continue
        r = new_result(B, key, s_row, smp); B["results"].append(r)

# --------------------------------------------------------------------------- scenarios (deviations / OOS)
DEVS = []
qa = emps("QA Reviewer")
def dev(B, typ, title, sev, opened, closed, cause, capa=None, trig=None, ex=None):
    d = dict(B=B, typ=typ, title=title, sev=sev, opened=opened, closed=closed, cause=cause, capa=capa, trig=trig, ex=ex, owner=rng.choice(qa))
    DEVS.append(d); B.setdefault("devs", []).append(d); return d
gmp_done = [B for B in BATCHES if B["gmp"] == "GMP" and B["steps"] and B["ds_end"] < NOW - 3 * DAY]
used = set()
def choose(cands):
    cands = [b for b in cands if b["num"] not in used]
    b = rng.choice(cands) if cands else None
    if b: used.add(b["num"])
    return b
def release_results(B): return [r for r in B["results"] if r["spec"]["stage"] == "Release"]
def pick_oos_key(B): return rng.choice(["HMW-DS", "MONO-DS", "HCP-DS", "ENDO-DS", "MAIN-DS"])
def get_res(B, key): return next(r for r in B["results"] if r["key"] == key)

# (1) confirmed OOS -> Rejected
B = choose([b for b in gmp_done if b["ds_end"] < NOW - 120 * DAY])
if B:
    r = get_res(B, pick_oos_key(B)); q, v = gen_oos(r["spec"]); r.update(q=q, v=v, out="OOS")
    op = r["tested"] + DAY; cl = op + dt.timedelta(days=rng.randint(20, 35))
    dev(B, "OOS Investigation", f"OOS {r['spec']['attribute']} - Drug Substance release", "Major", op, cl,
        "No assignable laboratory cause; result confirmed as product attribute", capa=f"CAPA-{op:%y}-{rng.randint(10,99)}", trig=r)
    B["scenario"] = "confirmed"
# (2) invalidated OOS -> retest -> Released (x2)
for _ in range(2):
    B = choose([b for b in gmp_done if b["ds_end"] < NOW - 80 * DAY])
    if not B: continue
    key = pick_oos_key(B); r = get_res(B, key); q, v = gen_oos(r["spec"]); r.update(q=q, v=v, out="OOS", status="Invalidated")
    op = r["tested"] + DAY
    rt = new_result(B, key, r["spec"], r["smp"], attempt=2, start_at=op + dt.timedelta(days=rng.randint(3, 6))); rt["orig"] = r
    B["results"].append(rt)
    cl = rt["reviewed"] + dt.timedelta(days=rng.randint(5, 12))
    CAUSES = {"HPLC": "Laboratory error: SEC column failed system suitability; run invalidated per SOP",
              "ELISA": "Laboratory error: plate washer dispense fault; run invalidated per SOP",
              "Capillary IEF": "Laboratory error: capillary cartridge beyond use-life; run invalidated per SOP",
              "Kinetic LAL": "Laboratory error: spike recovery outside 50-200%; run invalidated per SOP"}
    cause = CAUSES.get(ASSAYS[r["assay"]][1], "Laboratory error: incorrect sample dilution; run invalidated per SOP")
    dev(B, "OOS Investigation", f"OOS {r['spec']['attribute']} - Drug Substance release", "Major", op, cl,
        cause, capa=f"CAPA-{op:%y}-{rng.randint(10,99)}", trig=r)
    B["scenario"] = "invalidated"
# (3) open OOS -> Under Investigation
OOS_KEYS = ["HMW-DS", "MONO-DS", "HCP-DS", "ENDO-DS", "MAIN-DS"]
def oos_cands(b): return [r for r in release_results(b) if r["key"] in OOS_KEYS and r["tested"] < NOW - 2 * DAY]
B = choose([b for b in gmp_done if NOW - 100 * DAY < b["ds_end"] < NOW - 12 * DAY and oos_cands(b)])
if B:
    r = rng.choice(oos_cands(B)); q, v = gen_oos(r["spec"]); r.update(q=q, v=v, out="OOS")
    op = r["tested"] + DAY
    dev(B, "OOS Investigation", f"OOS {r['spec']['attribute']} - Drug Substance release", "Major", op, None, None, trig=r); B["scenario"] = "open_oos"
# process deviations
PROC = [("Low pH hold exceeded 60 min limit by 12 min", "Major", "Low pH Viral Inactivation", "Delayed neutralization; viral clearance impact assessment concluded no impact"),
        ("Viral filter integrity test failed on first attempt; filter replaced and retested passing", "Major", "Viral Filtration", "Incomplete filter wetting before test"),
        ("Protein A column pressure alarm; flow rate reduced per contingency", "Minor", "Protein A Affinity Capture", "Resin bed compression; column repacked before next use"),
        ("UF/DF transmembrane pressure excursion", "Minor", "Ultrafiltration/Diafiltration", "Pump speed set-point entered incorrectly"),
        ("Bioreactor pH excursion (+0.3 for 25 min)", "Minor", None, "CO2 sparge valve sticking; valve replaced")]
for k in range(3):
    B = choose([b for b in gmp_done if b["ds_end"] < NOW - 60 * DAY])
    if not B: continue
    title, sev, stname, cause = PROC[k]
    ex = next((e for e in B["steps"] if e["st"]["name"] == stname), None)
    op = (ex["start"] if ex else B["start"] + dt.timedelta(days=rng.randint(4, 9))) + dt.timedelta(hours=3)
    cl = op + dt.timedelta(days=rng.randint(12, 35)); capa = f"CAPA-{op:%y}-{rng.randint(10,99)}" if sev == "Major" else None
    dev(B, "Process Deviation", title, sev, op, cl, cause, capa=capa, ex=ex); B["scenario"] = "procdev"
# (4) open process deviation on a very recent batch
rec = [b for b in BATCHES if b["steps"] and b["num"] not in used and any(e["start"] < NOW - 2 * DAY for e in b["steps"]) and b["ds_end"] > NOW - 45 * DAY]
B = choose(rec)
if B:
    ex = next(e for e in B["steps"] if e["st"]["name"] in ("Viral Filtration", "Protein A Affinity Capture", "Low pH Viral Inactivation") and e["end"] < NOW)
    op = ex["start"] + dt.timedelta(hours=3)
    title, sev, _, cause = PROC[1] if ex["st"]["name"] == "Viral Filtration" else (PROC[2] if ex["st"]["name"] == "Protein A Affinity Capture" else PROC[0])
    dev(B, "Process Deviation", title, sev, op, None, None, ex=ex); B["scenario"] = "open_proc"

# --------------------------------------------------------------------------- statuses, cutoff truncation
def ex_visible(e): return e["start"] <= NOW
for B in BATCHES:
    B["role_ok"] = False
    # truncate results by cutoff
    keep = []
    for r in B["results"]:
        if r["tested"] > NOW: continue                      # not tested yet -> no record
        if r["reviewed"] > NOW: r["reviewed"] = None
        keep.append(r)
    B["results"] = keep
    # a retest requires its (invalidated) original
    B["results"] = [r for r in B["results"] if r["orig"] is None or r["orig"] in B["results"]]
    for d in B.get("devs", []):
        if d["closed"] and d["closed"] > NOW: d["closed"] = None
    open_dev = any(d["closed"] is None for d in B.get("devs", []))
    B["open_dev"] = open_dev
    if B["harvest"] > NOW: B["status"] = "In Culture"
    elif not B["steps"] or B["steps"][-1]["end"] > NOW: B["status"] = "Under Investigation" if (open_dev and B.get("scenario") == "open_proc") else "In Purification"
    else:
        rel_specs = [s for s in B["p"]["specs"].values() if s["stage"] == "Release"]
        rel = release_results(B); valid = [r for r in rel if r["status"] == "Valid"]
        have = {r["key"] for r in valid}
        complete = all(s["_key"] in have for s in rel_specs) and all(r["reviewed"] for r in valid)
        if open_dev: B["status"] = "Under Investigation"
        elif not complete: B["status"] = "Pending QC Testing"
        else:
            last = max([r["reviewed"] for r in rel if r["reviewed"]] + [d["closed"] for d in B.get("devs", []) if d["closed"]])
            disp = (last + dt.timedelta(days=rng.randint(2, 8))).replace(hour=0, minute=0, second=0)
            fail = any(r["out"] == "OOS" and r["status"] == "Valid" for r in rel)
            if disp > NOW: B["status"] = "Pending QA Review"
            else: B["status"] = "Rejected" if fail else "Released"; B["disp"] = disp
# Under Investigation with open deviation of OOS type but results all in -> fine.

# --------------------------------------------------------------------------- emit nodes & relationships
# Batch rows
for B in BATCHES:
    p = B["p"]; num = B["num"]
    row = dict(batchNumber=num, gmpStatus=B["gmp"], status=B["status"], scaleL=B["scale"], harvestVolumeL="", titerGPerL="",
               drugSubstanceG="", overallYieldPct="", dispositionDate="")
    if B["steps"]:
        row.update(harvestVolumeL=B["hv"], titerGPerL=B["titer"])
        if B["steps"][-1]["end"] <= NOW: row.update(drugSubstanceG=B["ds_g"], overallYieldPct=B["overall"])
    if B.get("disp"): row["dispositionDate"] = dts(B["disp"])
    addn("Batch", **row)
    addr("OF_PRODUCT", num, p["code"])
    wcb = [w for pr_, w in sorted(p["wcbs"]) if pr_ <= B["start"]][-1]
    addr("INOCULATED_FROM", num, wcb)
    addr("PRODUCES", B["br"]["equipmentId"], num, startTime=ts(B["start"]), endTime=ts(B["harvest"]) if B["harvest"] <= NOW else "",
         workingVolumeL=rd(B["br"]["nominalVolumeL"] * .8, 1))
    # people
    ups = rng.choice(emps("Upstream Operator")); dwn = rng.choice(emps("Downstream Operator"))
    sci = {"BTX-101": 0, "BTX-505": 0, "BTX-202": 1, "BTX-404": 1, "BTX-303": 2}[p["code"]]
    addr("RESPONSIBLE_FOR", ups["employeeId"], num, role="Upstream Lead")
    if B["steps"]: addr("RESPONSIBLE_FOR", dwn["employeeId"], num, role="Downstream Lead")
    addr("RESPONSIBLE_FOR", emps("Process Scientist")[sci]["employeeId"], num, role="Process Owner")
    if B.get("disp"): addr("RESPONSIBLE_FOR", rng.choice(qa)["employeeId"], num, role="QA Approver")
    B["dwn"] = dwn
    # upstream materials (at inoculation)
    wv = B["br"]["nominalVolumeL"] * .8
    for mid, qty, unit in [("MAT-001", rd(wv * .75, 0), "L"), ("MAT-002", rd(wv * .25, 0), "L"), ("MAT-003", rd(wv * .004, 1), "L")]:
        addr("CONSUMED", num, pick_lot(mid, B["start"])["lotNumber"], quantity=qty, unit=unit)
    # protocol & executions
    if B["proto"]:
        pr = B["proto"]
        addr("UNDERGOES", num, pr["id"], startTime=ts(B["steps"][0]["start"]) if B["steps"] else "",
             endTime=ts(B["steps"][-1]["end"]) if B["steps"] and B["steps"][-1]["end"] <= NOW else "")
        for e in B["steps"]:
            if e["start"] > NOW: break
            st = e["st"]; eid = f"{num}-S{st['number']:02d}"; e["id"] = eid; done = e["end"] <= NOW
            addn("StepExecution", executionId=eid, status="Completed" if done else "In Progress", startTime=ts(e["start"]),
                 endTime=ts(e["end"]) if done else "", stepYieldPct=e["yield_"] if done else "", poolVolumeL=e["vol"] if done else "")
            addr("PART_OF", eid, num); addr("OF_STEP", eid, st["stepId"])
            addr("EXECUTED_BY", eid, (dwn if rng.random() < .7 else rng.choice(emps("Downstream Operator")))["employeeId"])
            for mid in st["mats"]:
                need = {"MAT-010": ("EA", max(1, B["scale"] // 700 + 1)), "MAT-011": ("L", rd(.2 + B["scale"] / 150, 1)), "MAT-012": ("L", rd(.2 + B["scale"] / 180, 1)),
                        "MAT-013": ("L", rd(.2 + B["scale"] / 200, 1)), "MAT-014": ("L", rd(.2 + B["scale"] / 200, 1)), "MAT-015": ("EA", max(1, B["scale"] // 1000 + 1)),
                        "MAT-016": ("EA", max(1, B["scale"] // 500 + 1)), "MAT-017": ("EA", max(1, B["scale"] // 1000 + 1)),
                        "MAT-018": ("L", rd(B["scale"] * 1.5, 0)), "MAT-019": ("L", rd(B["scale"] * .1, 0)), "MAT-020": ("L", rd(B["scale"] * .8, 0))}[mid]
                addr("CONSUMED", num, pick_lot(mid, e["start"])["lotNumber"], quantity=need[1], unit=need[0])
    # samples
    n = 0
    for sp, smp in B["samples"].items():
        n += 1; sid = f"S-{num}-{n:02d}"; smp["id"] = sid
        addn("Sample", sampleId=sid, sampleType=smp["type"], samplePoint=sp, collectedAt=ts(smp["at"]),
             volumeMl=rd(U(5, 40), 0), storageCondition=rng.choice(["2-8C"] if smp["type"] == "In-Process" else ["-70C", "2-8C"]))
        addr("TAKEN_FROM", sid, num); addr("TAKEN_AT", sid, smp["ex"]["id"])

# results: id by test time
allres = sorted([r for B in BATCHES for r in B["results"]], key=lambda r: (r["tested"], r["B"]["num"], r["key"]))
for i, r in enumerate(allres, 1): r["id"] = f"R-{i:06d}"
for r in allres:
    B = r["B"]; lab = r["lab"]
    analysts = [e for e in emps("QC Analyst", lab)]; perf = rng.choice(analysts)
    rev = None
    if r["reviewed"]:
        rev = rng.choice([e for e in emps("QC Reviewer", lab) if e is not perf])
    addn("TestResult", resultId=r["id"], attempt=r["attempt"], qualifier=r["q"], value=r["v"], unit=r["unit"], outcome=r["out"],
         resultStatus=r["status"], testedAt=ts(r["tested"]), reviewedAt=ts(r["reviewed"]), reviewStatus="Reviewed" if rev else "Pending Review")
    addr("ON_SAMPLE", r["id"], r["smp"]["id"]); addr("USES_METHOD", r["id"], r["assay"]); addr("AGAINST_SPEC", r["id"], r["spec"]["specId"])
    addr("CONDUCTED_IN", r["id"], lab); addr("PERFORMED_BY", r["id"], perf["employeeId"])
    if rev: addr("REVIEWED_BY", r["id"], rev["employeeId"])
    itype, aux = ASSAYS[r["assay"]][2], ASSAYS[r["assay"]][3]
    if itype: addr("USED_FOR", rng.choice([i for i in INSTR if i["_lab"] == lab and i["instrumentType"] == itype])["instrumentId"], r["id"])
    for a in aux:
        c = [i for i in INSTR if i["_lab"] == lab and i["instrumentType"] == a]
        if c: addr("USED_FOR", rng.choice(c)["instrumentId"], r["id"])
    if r["orig"]: addr("RETEST_OF", r["id"], r["orig"]["id"])
# deviations
for i, d in enumerate(sorted(DEVS, key=lambda d: d["opened"]), 1):
    d["id"] = f"DEV-{d['opened']:%y}-{sum(1 for x in DEVS if x['opened'].year == d['opened'].year and x['opened'] <= d['opened']):03d}"
for d in sorted(DEVS, key=lambda d: d["id"]):
    closed = d["closed"]
    addn("Deviation", deviationId=d["id"], deviationType=d["typ"], title=d["title"], severity=d["sev"],
         status="Closed" if closed else "Open", openedDate=dts(d["opened"]), closedDate=dts(closed) if closed else "",
         rootCause=(d["cause"] if closed else ""), capaNumber=(d["capa"] if closed and d["capa"] else ""))
    addr("AFFECTS", d["id"], d["B"]["num"]); addr("OWNED_BY", d["id"], d["owner"]["employeeId"])
    if d["trig"]: addr("TRIGGERED_BY", d["id"], d["trig"]["id"])
    if d["ex"]: addr("OCCURRED_AT", d["id"], d["ex"]["id"])

# --------------------------------------------------------------------------- write CSVs
def fmt(v):
    if v is None: return ""
    if isinstance(v, float): return repr(round(v, 6))
    return str(v)
def write(out):
    os.makedirs(out, exist_ok=True)
    for label, n in spec.NODES.items():
        cols = [p[0] for p in n["props"]]
        with open(os.path.join(out, n["file"]), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(cols)
            for row in NODES[label]: w.writerow([fmt(row.get(c, "")) for c in cols])
    for r in spec.RELS:
        fc, tc = spec.rel_cols(r); props = [p[0] for p in r["props"]]
        with open(os.path.join(out, r["file"]), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow([fc, tc] + props)
            for row in RELS[r["type"]]: w.writerow([row["_a"], row["_b"]] + [fmt(row.get(c, "")) for c in props])
if __name__ == "__main__":
    out = sys.argv[1]; write(out)
    print({k: len(v) for k, v in NODES.items()}); print({k: len(v) for k, v in RELS.items()})
    from collections import Counter
    print(Counter(b["status"] for b in BATCHES), Counter(b.get("scenario") for b in BATCHES))
