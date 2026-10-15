"""
Single source of truth for the v2 model.

Everything else (CSV writer, importer JSON, validator, Cypher helpers) is generated
from NODES / RELS below, so the files cannot drift apart.

Conventions
  * CSV column name == graph property name, always (no id_id / lab_id_location renames).
  * Each label has exactly ONE key property (natural business key where one exists).
    The key gets ONE uniqueness constraint. Extra `unique` props only where the real
    world guarantees it (employee e-mail, product code...).
  * No standalone indexes that duplicate a constraint (that was the v1 error).
  * Types limited to string / integer / float / datetime (what the v1 file already used).
"""

# prop tuple: (name, type, required)
S, I, F, D = "string", "integer", "float", "datetime"

NODES = {
 "Lab": dict(file="labs.csv", key="labId", props=[
    ("labId", S, 1), ("name", S, 1), ("department", S, 0), ("building", S, 0), ("gxpScope", S, 0)]),
 "Employee": dict(file="employees.csv", key="employeeId", unique=["email"], props=[
    ("employeeId", S, 1), ("name", S, 1), ("email", S, 1), ("role", S, 1), ("department", S, 0)]),
 "Product": dict(file="products.csv", key="productCode", props=[
    ("productCode", S, 1), ("modality", S, 1), ("targetAntigen", S, 0), ("isotype", S, 0),
    ("molecularWeightKDa", F, 0), ("developmentPhase", S, 0), ("formulation", S, 0)]),
 "CellBank": dict(file="cell_banks.csv", key="bankId", props=[
    ("bankId", S, 1), ("bankType", S, 1), ("cellLine", S, 1), ("passageNumber", I, 0),
    ("vialCount", I, 0), ("preparedDate", D, 0), ("status", S, 0)]),
 "Bioreactor": dict(file="bioreactors.csv", key="equipmentId", props=[
    ("equipmentId", S, 1), ("type", S, 0), ("manufacturer", S, 0), ("model", S, 0),
    ("nominalVolumeL", I, 1), ("location", S, 0), ("status", S, 0), ("qualifiedDate", D, 0)]),
 "Batch": dict(file="batches.csv", key="batchNumber", props=[
    ("batchNumber", S, 1), ("gmpStatus", S, 1), ("status", S, 1), ("scaleL", I, 1),
    ("harvestVolumeL", F, 0), ("titerGPerL", F, 0), ("drugSubstanceG", F, 0),
    ("overallYieldPct", F, 0), ("dispositionDate", D, 0)]),
 "PurificationProtocol": dict(file="purification_protocols.csv", key="protocolId", props=[
    ("protocolId", S, 1), ("documentNumber", S, 1), ("name", S, 1), ("version", S, 1),
    ("status", S, 1), ("effectiveDate", D, 1), ("supersededDate", D, 0), ("description", S, 0)]),
 "PurificationStep": dict(file="purification_steps.csv", key="stepId", props=[
    ("stepId", S, 1), ("stepNumber", I, 1), ("stepName", S, 1), ("stepType", S, 1),
    ("operatingParameters", S, 0)]),
 "StepExecution": dict(file="step_executions.csv", key="executionId", props=[
    ("executionId", S, 1), ("status", S, 1), ("startTime", D, 1), ("endTime", D, 0),
    ("stepYieldPct", F, 0), ("poolVolumeL", F, 0)]),
 "Material": dict(file="materials.csv", key="materialId", props=[
    ("materialId", S, 1), ("name", S, 1), ("category", S, 1), ("supplier", S, 0), ("grade", S, 0)]),
 "MaterialLot": dict(file="material_lots.csv", key="lotNumber", props=[
    ("lotNumber", S, 1), ("supplierLotNumber", S, 0), ("receivedDate", D, 1), ("expiryDate", D, 1),
    ("status", S, 1)]),
 "Sample": dict(file="samples.csv", key="sampleId", props=[
    ("sampleId", S, 1), ("sampleType", S, 1), ("samplePoint", S, 1), ("collectedAt", D, 1),
    ("volumeMl", F, 0), ("storageCondition", S, 0)]),
 "Assay": dict(file="assays.csv", key="methodId", props=[
    ("methodId", S, 1), ("name", S, 1), ("technique", S, 1), ("version", S, 1), ("status", S, 1),
    ("instrumentType", S, 0), ("description", S, 0)]),
 "Specification": dict(file="specifications.csv", key="specId", props=[
    ("specId", S, 1), ("attribute", S, 1), ("category", S, 0), ("stage", S, 1), ("samplePoint", S, 1),
    ("unit", S, 0), ("limitType", S, 1), ("lowerLimit", F, 0), ("upperLimit", F, 0)]),
 "Instrument": dict(file="instruments.csv", key="instrumentId", props=[
    ("instrumentId", S, 1), ("name", S, 1), ("instrumentType", S, 1), ("manufacturer", S, 0),
    ("model", S, 0), ("status", S, 0), ("lastCalibrated", D, 0), ("calibrationDue", D, 0)]),
 "TestResult": dict(file="test_results.csv", key="resultId", props=[
    ("resultId", S, 1), ("attempt", I, 1), ("qualifier", S, 0), ("value", F, 0), ("unit", S, 0),
    ("outcome", S, 1), ("resultStatus", S, 1), ("testedAt", D, 1), ("reviewedAt", D, 0),
    ("reviewStatus", S, 1)]),
 "Deviation": dict(file="deviations.csv", key="deviationId", props=[
    ("deviationId", S, 1), ("deviationType", S, 1), ("title", S, 1), ("severity", S, 1),
    ("status", S, 1), ("openedDate", D, 1), ("closedDate", D, 0), ("rootCause", S, 0),
    ("capaNumber", S, 0)]),
}

# (type, from_label, to_label, file, props, from_col, to_col)
# Columns default to the endpoint key property names; when both ends share a label they are prefixed.
def _r(t, a, b, f, props=(), fc=None, tc=None):
    return dict(type=t, frm=a, to=b, file=f, props=list(props), fc=fc, tc=tc)

RELS = [
 _r("WORKS_IN", "Employee", "Lab", "works_in.csv"),
 _r("LOCATED_IN", "Instrument", "Lab", "located_in.csv"),
 _r("EXPRESSES", "CellBank", "Product", "expresses.csv"),
 _r("DERIVED_FROM", "CellBank", "CellBank", "derived_from.csv", fc="bankId", tc="parentBankId"),
 _r("OF_PRODUCT", "Batch", "Product", "of_product.csv"),
 _r("INOCULATED_FROM", "Batch", "CellBank", "inoculated_from.csv"),
 _r("PRODUCES", "Bioreactor", "Batch", "produces.csv",
    [("startTime", D, 1), ("endTime", D, 0), ("workingVolumeL", F, 0)]),
 _r("UNDERGOES", "Batch", "PurificationProtocol", "undergoes.csv",
    [("startTime", D, 1), ("endTime", D, 0)]),
 _r("INCLUDES", "PurificationProtocol", "PurificationStep", "includes.csv"),
 _r("FOLLOWED_BY", "PurificationStep", "PurificationStep", "followed_by.csv", fc="stepId", tc="nextStepId"),
 _r("SUPERSEDES", "PurificationProtocol", "PurificationProtocol", "supersedes.csv", fc="protocolId", tc="supersededProtocolId"),
 _r("REQUIRES", "PurificationStep", "Material", "requires.csv"),
 _r("LOT_OF", "MaterialLot", "Material", "lot_of.csv"),
 _r("CONSUMED", "Batch", "MaterialLot", "consumed.csv", [("quantity", F, 1), ("unit", S, 1)]),
 _r("PART_OF", "StepExecution", "Batch", "part_of.csv"),
 _r("OF_STEP", "StepExecution", "PurificationStep", "of_step.csv"),
 _r("EXECUTED_BY", "StepExecution", "Employee", "executed_by.csv"),
 _r("RESPONSIBLE_FOR", "Employee", "Batch", "responsible_for.csv", [("role", S, 1)]),
 _r("TAKEN_FROM", "Sample", "Batch", "taken_from.csv"),
 _r("TAKEN_AT", "Sample", "StepExecution", "taken_at.csv"),
 _r("ON_SAMPLE", "TestResult", "Sample", "on_sample.csv"),
 _r("USES_METHOD", "TestResult", "Assay", "uses_method.csv"),
 _r("AGAINST_SPEC", "TestResult", "Specification", "against_spec.csv"),
 _r("CONDUCTED_IN", "TestResult", "Lab", "conducted_in.csv"),
 _r("PERFORMED_BY", "TestResult", "Employee", "performed_by.csv"),
 _r("REVIEWED_BY", "TestResult", "Employee", "reviewed_by.csv"),
 _r("USED_FOR", "Instrument", "TestResult", "used_for.csv"),
 _r("RETEST_OF", "TestResult", "TestResult", "retest_of.csv", fc="resultId", tc="originalResultId"),
 _r("APPLIES_TO", "Specification", "Product", "applies_to.csv"),
 _r("MEASURED_BY", "Specification", "Assay", "measured_by.csv"),
 _r("AFFECTS", "Deviation", "Batch", "affects.csv"),
 _r("TRIGGERED_BY", "Deviation", "TestResult", "triggered_by.csv"),
 _r("OCCURRED_AT", "Deviation", "StepExecution", "occurred_at.csv"),
 _r("OWNED_BY", "Deviation", "Employee", "owned_by.csv"),
]

def rel_cols(r):
    fc = r["fc"] or NODES[r["frm"]]["key"]
    tc = r["tc"] or NODES[r["to"]]["key"]
    return fc, tc

# Fixed-vocabulary properties (checked by validator; also documents the model)
ENUMS = {
 ("Employee", "role"): {"Upstream Operator", "Downstream Operator", "Process Scientist", "QC Analyst", "QC Reviewer", "QA Reviewer"},
 ("Batch", "status"): {"In Culture", "In Purification", "Pending QC Testing", "Pending QA Review", "Under Investigation", "Released", "Rejected"},
 ("Batch", "gmpStatus"): {"GMP", "Non-GMP"},
 ("StepExecution", "status"): {"In Progress", "Completed"},
 ("MaterialLot", "status"): {"Approved", "Quarantine", "Rejected", "Supplier Notification"},
 ("TestResult", "outcome"): {"Conforms", "OOS", "Reported"},
 ("TestResult", "resultStatus"): {"Valid", "Invalidated"},
 ("TestResult", "reviewStatus"): {"Reviewed", "Pending Review"},
 ("Specification", "limitType"): {"NMT", "NLT", "Range", "Report"},
 ("Deviation", "status"): {"Open", "Closed"},
 ("Deviation", "severity"): {"Minor", "Major", "Critical"},
 ("Deviation", "deviationType"): {"OOS Investigation", "Process Deviation"},
 ("PurificationProtocol", "status"): {"Effective", "Superseded"},
}

# Model names from the ORIGINAL file, so reset.cypher can clean up a half-loaded v1 database
V1_CONSTRAINT_AND_INDEX_NAMES_FILE = "neo4j_importer_model.json"
