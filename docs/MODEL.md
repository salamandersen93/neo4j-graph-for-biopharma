# Data model

Synthetic drug-substance manufacturing for CHO-derived biologics: cell banks, bioreactor runs, versioned purification
recipes and their executions, material lots, QC samples and results against specifications, and GxP deviations.
The model is defined once in `model/spec.py`; the CSVs, the Aura importer file, the validator and the Cypher helpers are all generated from it.

| Area | Nodes | Key property |
|---|---|---|
| Product and cell line | Product, CellBank (MCB to WCB) | productCode, bankId |
| Upstream | Bioreactor, Batch | equipmentId, batchNumber |
| Recipe vs execution | PurificationProtocol (versioned), PurificationStep, StepExecution | protocolId, stepId, executionId |
| Materials | Material, MaterialLot | materialId, lotNumber |
| QC | Sample, TestResult, Specification, Assay, Instrument, Lab | sampleId, resultId, specId, methodId, instrumentId, labId |
| Quality events | Deviation | deviationId |
| People | Employee (role-based) | employeeId |

Core paths
- `(Bioreactor)-[:PRODUCES]->(Batch)-[:UNDERGOES]->(PurificationProtocol)-[:INCLUDES]->(PurificationStep)`
- `(StepExecution)-[:PART_OF]->(Batch)` and `-[:OF_STEP]->(PurificationStep)`
- `(Sample)-[:TAKEN_AT]->(StepExecution)`; `(TestResult)-[:ON_SAMPLE]->(Sample)`, `-[:AGAINST_SPEC]->(Specification)`, `-[:USES_METHOD]->(Assay)`
- `(Deviation)-[:AFFECTS]->(Batch)`, `-[:TRIGGERED_BY]->(TestResult)`
- `(Batch)-[:CONSUMED {quantity, unit}]->(MaterialLot)-[:LOT_OF]->(Material)`

Modelling decisions
- **Master data vs record.** Protocol and step are the controlled recipe (versioned, one effective at a time). StepExecution is what actually ran: times, step yield, pool volume, operator.
- **Specifications are data.** Limits live on `Specification` per product, attribute and sample point; `TestResult.outcome` is derived from them and the validator re-derives it.
- **Chain of custody.** Every result has a performer and a different reviewer; instruments must be in the conducting lab and match the method.
- **OOS handling.** Invalidated OOS plus a retest (`RETEST_OF`); confirmed OOS leads to Rejected; an open investigation leads to Under Investigation.
- **Natural keys.** One key property per label, one uniqueness constraint per key (plus Employee.email). No standalone indexes that duplicate a constraint, and no existence constraints in the importer file.

## Why v1 failed to load (history)
The original agent-generated model declared 20 standalone indexes whose names were identical to uniqueness constraints, so the second `CREATE` of each
pair failed with an "already exists" error. `src/check_importer_json.py` detects this class of problem, and `model/legacy_v1_names.json` lets `cypher/reset.cypher` clean up a database that a v1 attempt left half-built.

## Business rules the validator enforces
Outcome recomputes from value and limits; a released batch has all release results conforming, no open deviation and one QA approver; no overlapping bioreactor runs;
the protocol was effective when executed; consumed lots were approved and unexpired at use; step yields multiply to the overall yield; a reviewer is never the performer; and more (`src/validate.py`).

## Not modelled
Seed train and media preparation, column packing, equipment cleaning status, calibration history (only current status), stability, environmental monitoring, audit trail and electronic signatures.
Limits, yields and distributions are plausible, not taken from any real filing. Products (BTX-xxx) and the company are fictional; vendor and model names on equipment are real products used as labels.
