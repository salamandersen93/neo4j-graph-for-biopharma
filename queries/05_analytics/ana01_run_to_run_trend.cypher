// @id: ANA-01
// @title: Run-to-run trend without window functions
// @level: advanced
// @neo4j: 5.x
// @writes: false
// @learn: ORDER BY, then collect(), then a list comprehension over range() replaces LAG() for simple deltas.
// @biopharma: Trending yield across consecutive batches surfaces step changes after a process or material change,
//   which is the core of continued process verification.
// @expect: One row per product with completed batches: the yield list in start order and the batch-to-batch
//   deltas.
// ---
MATCH (p:Product)<-[:OF_PRODUCT]-(b:Batch)<-[r:PRODUCES]-()
WHERE b.overallYieldPct IS NOT NULL
WITH p, b, r ORDER BY r.startTime
WITH p, collect(b.overallYieldPct) AS y
RETURN p.productCode, y, [i IN range(1, size(y)-1) | round(y[i] - y[i-1], 1)] AS deltas;
