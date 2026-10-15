// @id: F-11
// @title: ORDER BY, SKIP, LIMIT and where nulls sort
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: ORDER BY sorts nulls last in ascending order and first in descending order; SKIP and LIMIT page the result
//   (SKIP, not OFFSET), and a second sort key makes paging deterministic.
// @biopharma: 'Top five yielding batches' reports are common in product reviews; a top-N list that is led by missing values is
//   a wrong report, not a cosmetic one.
// @expect: Statement 1: five rows led by three null yields (BTX101-26-003, BTX303-26-003, BTX505-26-004) then 80.0 and
//   77.6. Statement 2: the top five real yields starting with 80.0.
// @pitfall: Descending order puts nulls first, which surprises people coming from databases that sort nulls last. Filter
//   with IS NOT NULL or sort on coalesce(x, -1). Without a tie-breaker, rows with equal keys may come back in a
//   different order between runs.
// @docs: Cypher manual: Clauses > ORDER BY, SKIP, LIMIT; Working with null (ordering).
// ---
MATCH (b:Batch)
RETURN b.batchNumber AS batch, b.overallYieldPct AS yield
ORDER BY yield DESC, batch
LIMIT 5;

MATCH (b:Batch)
WHERE b.overallYieldPct IS NOT NULL
RETURN b.batchNumber AS batch, b.overallYieldPct AS yield
ORDER BY yield DESC, batch
SKIP 0 LIMIT 5;
