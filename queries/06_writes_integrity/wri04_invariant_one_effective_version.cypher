// @id: WRI-04
// @title: Check an invariant the database cannot enforce
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: Cypher constraints cannot express "exactly one"; a grouped query that returns violations does, and
//   it can run on a schedule.
// @biopharma: Cardinality rules on controlled documents (one effective version per document number) are data-
//   quality monitors. Schedule the query and alert on any returned row.
// @expect: 0 rows, both before and after WRI-03. To see it fire, run WRI-03 without its SET line.
// ---
MATCH (p:PurificationProtocol {status:'Effective'})
WITH p.documentNumber AS doc, collect(p.protocolId) AS effective
WHERE size(effective) <> 1
RETURN doc, effective;
