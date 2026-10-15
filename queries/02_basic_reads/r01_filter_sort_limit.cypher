// @id: R-01
// @title: Filter, sort, limit
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: Inline property maps filter on equality; the relationship pattern replaces the SQL join.
// @biopharma: Pulling the release history of a product is the raw input to an annual product review and to
//   continued process verification.
// @expect: 5 rows, newest disposition first.
// ---
MATCH (b:Batch {status:'Released'})-[:OF_PRODUCT]->(:Product {productCode:'BTX-101'})
RETURN b.batchNumber, b.scaleL, b.titerGPerL, b.overallYieldPct, b.dispositionDate
ORDER BY b.dispositionDate DESC LIMIT 5;
