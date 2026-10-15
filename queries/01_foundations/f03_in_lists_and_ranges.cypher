// @id: F-03
// @title: IN with lists and chained range comparisons
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: IN tests membership of a list literal, and comparisons chain (200 <= x <= 500), so a range needs no AND.
// @biopharma: Scale classes (50 L bench, 200 L development, 500 L pilot, 2000 L production) are natural lists and ranges;
//   filtering on them is how comparability and scale-up reviews are scoped.
// @expect: Three rows: (200, Rejected, 1), (200, Released, 3), (500, Released, 9).
// @pitfall: IN needs a list, not a parenthesised set: b.status IN ('Released') is not a list. A list that contains null
//   never makes IN true for a null value.
// @docs: Cypher manual: Predicates > List operators (IN); Operators > Comparison operators (chained).
// ---
MATCH (b:Batch)
WHERE 200 <= b.scaleL <= 500
  AND b.status IN ['Released', 'Rejected']
RETURN b.scaleL AS scaleL, b.status AS status, count(*) AS batches
ORDER BY scaleL, status;
