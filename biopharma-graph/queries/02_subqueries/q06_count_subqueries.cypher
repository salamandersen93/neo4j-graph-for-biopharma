// @id: Q06
// @title: Count subqueries
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: COUNT { pattern } counts matches per row without multiplying rows - the modern replacement for
//   OPTIONAL MATCH followed by count().
// @biopharma: Batch record review is review-by-exception: you want to see quickly which batches carry deviations
//   and how much testing exists per batch.
// @expect: 10 rows; batches with deviations first.
// ---
MATCH (b:Batch)
RETURN b.batchNumber AS batch, b.status AS status,
       COUNT { (b)<-[:AFFECTS]-(:Deviation) } AS deviations,
       COUNT { (b)<-[:TAKEN_FROM]-(:Sample) } AS samples
ORDER BY deviations DESC, batch LIMIT 10;
