// @id: SUB-02
// @title: Collect subquery: OOS attributes per batch
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: COLLECT { MATCH ... RETURN x } builds a per-row list; filtering on size() of that list keeps only
//   rows that have matches.
// @biopharma: Out-of-specification results must be investigated before disposition (FDA guidance on investigating
//   OOS results). A per-batch OOS summary is what a disposition meeting looks at; invalidated results
//   appear next to confirmed ones so nothing is hidden.
// @expect: 4 batches: two Released (OOS invalidated, retest passed), one Rejected (confirmed), one Under
//   Investigation (open).
// ---
MATCH (b:Batch)
WITH b, COLLECT {
  MATCH (b)<-[:TAKEN_FROM]-(:Sample)<-[:ON_SAMPLE]-(t:TestResult {outcome:'OOS'})-[:AGAINST_SPEC]->(s:Specification)
  RETURN s.attribute + ' (' + t.resultStatus + ')'
} AS oosAttributes
WHERE size(oosAttributes) > 0
RETURN b.batchNumber, b.status, oosAttributes;
