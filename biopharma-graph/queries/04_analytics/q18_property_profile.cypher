// @id: Q18
// @title: Profile property coverage
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: keys(n) returns the property names present on a node; unwinding and counting profiles completeness
//   for any label.
// @biopharma: Completeness profiling is the first step in judging a data product's fitness for use. Structural
//   gaps (an in-process batch has no drug-substance mass yet) differ from quality gaps (a released batch
//   missing its disposition date).
// @expect: 9 rows, one per Batch property. batchNumber, gmpStatus, status and scaleL are on all 29 batches;
//   harvestVolumeL (28), drugSubstanceG (26), overallYieldPct (26) and dispositionDate (23) are lower
//   because in-flight batches do not have them yet.
// ---
MATCH (b:Batch) UNWIND keys(b) AS k RETURN k, count(*) AS populated ORDER BY populated;
