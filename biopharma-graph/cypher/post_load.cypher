// post_load.cypher - run AFTER the importer finishes. Everything is idempotent (IF NOT EXISTS).

// ===== A. Row-count verification (compare with the numbers in the comments) =====
MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS nodes ORDER BY label;
//   Lab                    4
//   Employee               28
//   Product                5
//   CellBank               11
//   Bioreactor             9
//   Batch                  29
//   PurificationProtocol   9
//   PurificationStep       73
//   StepExecution          221
//   Material               14
//   MaterialLot            103
//   Sample                 134
//   Assay                  10
//   Specification          95
//   Instrument             17
//   TestResult             492
//   Deviation              8
MATCH ()-[r]->() RETURN type(r) AS relationship, count(*) AS rels ORDER BY relationship;
//   WORKS_IN               14
//   LOCATED_IN             17
//   EXPRESSES              5
//   DERIVED_FROM           6
//   OF_PRODUCT             29
//   INOCULATED_FROM        29
//   PRODUCES               29
//   UNDERGOES              28
//   INCLUDES               73
//   FOLLOWED_BY            64
//   SUPERSEDES             4
//   REQUIRES               91
//   LOT_OF                 103
//   CONSUMED               363
//   PART_OF                221
//   OF_STEP                221
//   EXECUTED_BY            221
//   RESPONSIBLE_FOR        109
//   TAKEN_FROM             134
//   TAKEN_AT               134
//   ON_SAMPLE              492
//   USES_METHOD            492
//   AGAINST_SPEC           492
//   CONDUCTED_IN           492
//   PERFORMED_BY           492
//   REVIEWED_BY            486
//   USED_FOR               544
//   RETEST_OF              2
//   APPLIES_TO             95
//   MEASURED_BY            95
//   AFFECTS                8
//   TRIGGERED_BY           4
//   OCCURRED_AT            4
//   OWNED_BY               8

// ===== B. Optional: NOT NULL (existence) constraints =====
// Property existence constraints are an Enterprise feature; if your tier rejects them, skip this block - the importer
// mapping + validate.py already guarantee required values.  (They were part of the original model and are NOT in the importer file.)
CREATE CONSTRAINT `Lab_labId_exists` IF NOT EXISTS FOR (n:Lab) REQUIRE n.labId IS NOT NULL;
CREATE CONSTRAINT `Lab_name_exists` IF NOT EXISTS FOR (n:Lab) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `Employee_employeeId_exists` IF NOT EXISTS FOR (n:Employee) REQUIRE n.employeeId IS NOT NULL;
CREATE CONSTRAINT `Employee_name_exists` IF NOT EXISTS FOR (n:Employee) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `Employee_email_exists` IF NOT EXISTS FOR (n:Employee) REQUIRE n.email IS NOT NULL;
CREATE CONSTRAINT `Employee_role_exists` IF NOT EXISTS FOR (n:Employee) REQUIRE n.role IS NOT NULL;
CREATE CONSTRAINT `Product_productCode_exists` IF NOT EXISTS FOR (n:Product) REQUIRE n.productCode IS NOT NULL;
CREATE CONSTRAINT `Product_modality_exists` IF NOT EXISTS FOR (n:Product) REQUIRE n.modality IS NOT NULL;
CREATE CONSTRAINT `CellBank_bankId_exists` IF NOT EXISTS FOR (n:CellBank) REQUIRE n.bankId IS NOT NULL;
CREATE CONSTRAINT `CellBank_bankType_exists` IF NOT EXISTS FOR (n:CellBank) REQUIRE n.bankType IS NOT NULL;
CREATE CONSTRAINT `CellBank_cellLine_exists` IF NOT EXISTS FOR (n:CellBank) REQUIRE n.cellLine IS NOT NULL;
CREATE CONSTRAINT `Bioreactor_equipmentId_exists` IF NOT EXISTS FOR (n:Bioreactor) REQUIRE n.equipmentId IS NOT NULL;
CREATE CONSTRAINT `Bioreactor_nominalVolumeL_exists` IF NOT EXISTS FOR (n:Bioreactor) REQUIRE n.nominalVolumeL IS NOT NULL;
CREATE CONSTRAINT `Batch_batchNumber_exists` IF NOT EXISTS FOR (n:Batch) REQUIRE n.batchNumber IS NOT NULL;
CREATE CONSTRAINT `Batch_gmpStatus_exists` IF NOT EXISTS FOR (n:Batch) REQUIRE n.gmpStatus IS NOT NULL;
CREATE CONSTRAINT `Batch_status_exists` IF NOT EXISTS FOR (n:Batch) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `Batch_scaleL_exists` IF NOT EXISTS FOR (n:Batch) REQUIRE n.scaleL IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_protocolId_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.protocolId IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_documentNumber_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.documentNumber IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_name_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_version_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.version IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_status_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `PurificationProtocol_effectiveDate_exists` IF NOT EXISTS FOR (n:PurificationProtocol) REQUIRE n.effectiveDate IS NOT NULL;
CREATE CONSTRAINT `PurificationStep_stepId_exists` IF NOT EXISTS FOR (n:PurificationStep) REQUIRE n.stepId IS NOT NULL;
CREATE CONSTRAINT `PurificationStep_stepNumber_exists` IF NOT EXISTS FOR (n:PurificationStep) REQUIRE n.stepNumber IS NOT NULL;
CREATE CONSTRAINT `PurificationStep_stepName_exists` IF NOT EXISTS FOR (n:PurificationStep) REQUIRE n.stepName IS NOT NULL;
CREATE CONSTRAINT `PurificationStep_stepType_exists` IF NOT EXISTS FOR (n:PurificationStep) REQUIRE n.stepType IS NOT NULL;
CREATE CONSTRAINT `StepExecution_executionId_exists` IF NOT EXISTS FOR (n:StepExecution) REQUIRE n.executionId IS NOT NULL;
CREATE CONSTRAINT `StepExecution_status_exists` IF NOT EXISTS FOR (n:StepExecution) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `StepExecution_startTime_exists` IF NOT EXISTS FOR (n:StepExecution) REQUIRE n.startTime IS NOT NULL;
CREATE CONSTRAINT `Material_materialId_exists` IF NOT EXISTS FOR (n:Material) REQUIRE n.materialId IS NOT NULL;
CREATE CONSTRAINT `Material_name_exists` IF NOT EXISTS FOR (n:Material) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `Material_category_exists` IF NOT EXISTS FOR (n:Material) REQUIRE n.category IS NOT NULL;
CREATE CONSTRAINT `MaterialLot_lotNumber_exists` IF NOT EXISTS FOR (n:MaterialLot) REQUIRE n.lotNumber IS NOT NULL;
CREATE CONSTRAINT `MaterialLot_receivedDate_exists` IF NOT EXISTS FOR (n:MaterialLot) REQUIRE n.receivedDate IS NOT NULL;
CREATE CONSTRAINT `MaterialLot_expiryDate_exists` IF NOT EXISTS FOR (n:MaterialLot) REQUIRE n.expiryDate IS NOT NULL;
CREATE CONSTRAINT `MaterialLot_status_exists` IF NOT EXISTS FOR (n:MaterialLot) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `Sample_sampleId_exists` IF NOT EXISTS FOR (n:Sample) REQUIRE n.sampleId IS NOT NULL;
CREATE CONSTRAINT `Sample_sampleType_exists` IF NOT EXISTS FOR (n:Sample) REQUIRE n.sampleType IS NOT NULL;
CREATE CONSTRAINT `Sample_samplePoint_exists` IF NOT EXISTS FOR (n:Sample) REQUIRE n.samplePoint IS NOT NULL;
CREATE CONSTRAINT `Sample_collectedAt_exists` IF NOT EXISTS FOR (n:Sample) REQUIRE n.collectedAt IS NOT NULL;
CREATE CONSTRAINT `Assay_methodId_exists` IF NOT EXISTS FOR (n:Assay) REQUIRE n.methodId IS NOT NULL;
CREATE CONSTRAINT `Assay_name_exists` IF NOT EXISTS FOR (n:Assay) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `Assay_technique_exists` IF NOT EXISTS FOR (n:Assay) REQUIRE n.technique IS NOT NULL;
CREATE CONSTRAINT `Assay_version_exists` IF NOT EXISTS FOR (n:Assay) REQUIRE n.version IS NOT NULL;
CREATE CONSTRAINT `Assay_status_exists` IF NOT EXISTS FOR (n:Assay) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `Specification_specId_exists` IF NOT EXISTS FOR (n:Specification) REQUIRE n.specId IS NOT NULL;
CREATE CONSTRAINT `Specification_attribute_exists` IF NOT EXISTS FOR (n:Specification) REQUIRE n.attribute IS NOT NULL;
CREATE CONSTRAINT `Specification_stage_exists` IF NOT EXISTS FOR (n:Specification) REQUIRE n.stage IS NOT NULL;
CREATE CONSTRAINT `Specification_samplePoint_exists` IF NOT EXISTS FOR (n:Specification) REQUIRE n.samplePoint IS NOT NULL;
CREATE CONSTRAINT `Specification_limitType_exists` IF NOT EXISTS FOR (n:Specification) REQUIRE n.limitType IS NOT NULL;
CREATE CONSTRAINT `Instrument_instrumentId_exists` IF NOT EXISTS FOR (n:Instrument) REQUIRE n.instrumentId IS NOT NULL;
CREATE CONSTRAINT `Instrument_name_exists` IF NOT EXISTS FOR (n:Instrument) REQUIRE n.name IS NOT NULL;
CREATE CONSTRAINT `Instrument_instrumentType_exists` IF NOT EXISTS FOR (n:Instrument) REQUIRE n.instrumentType IS NOT NULL;
CREATE CONSTRAINT `TestResult_resultId_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.resultId IS NOT NULL;
CREATE CONSTRAINT `TestResult_attempt_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.attempt IS NOT NULL;
CREATE CONSTRAINT `TestResult_outcome_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.outcome IS NOT NULL;
CREATE CONSTRAINT `TestResult_resultStatus_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.resultStatus IS NOT NULL;
CREATE CONSTRAINT `TestResult_testedAt_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.testedAt IS NOT NULL;
CREATE CONSTRAINT `TestResult_reviewStatus_exists` IF NOT EXISTS FOR (n:TestResult) REQUIRE n.reviewStatus IS NOT NULL;
CREATE CONSTRAINT `Deviation_deviationId_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.deviationId IS NOT NULL;
CREATE CONSTRAINT `Deviation_deviationType_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.deviationType IS NOT NULL;
CREATE CONSTRAINT `Deviation_title_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.title IS NOT NULL;
CREATE CONSTRAINT `Deviation_severity_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.severity IS NOT NULL;
CREATE CONSTRAINT `Deviation_status_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.status IS NOT NULL;
CREATE CONSTRAINT `Deviation_openedDate_exists` IF NOT EXISTS FOR (n:Deviation) REQUIRE n.openedDate IS NOT NULL;

// ===== C. Lookup indexes for the common questions (named *_idx so they can never collide with a constraint) =====
CREATE INDEX `Batch_status_idx` IF NOT EXISTS FOR (n:Batch) ON (n.status);
CREATE INDEX `Batch_gmpStatus_idx` IF NOT EXISTS FOR (n:Batch) ON (n.gmpStatus);
CREATE INDEX `TestResult_outcome_idx` IF NOT EXISTS FOR (n:TestResult) ON (n.outcome);
CREATE INDEX `TestResult_testedAt_idx` IF NOT EXISTS FOR (n:TestResult) ON (n.testedAt);
CREATE INDEX `TestResult_reviewStatus_idx` IF NOT EXISTS FOR (n:TestResult) ON (n.reviewStatus);
CREATE INDEX `Sample_samplePoint_idx` IF NOT EXISTS FOR (n:Sample) ON (n.samplePoint);
CREATE INDEX `Deviation_status_idx` IF NOT EXISTS FOR (n:Deviation) ON (n.status);
CREATE INDEX `MaterialLot_status_idx` IF NOT EXISTS FOR (n:MaterialLot) ON (n.status);
CREATE INDEX `Specification_attribute_idx` IF NOT EXISTS FOR (n:Specification) ON (n.attribute);
CREATE INDEX `StepExecution_status_idx` IF NOT EXISTS FOR (n:StepExecution) ON (n.status);

// Example queries live in queries/ (see README).
