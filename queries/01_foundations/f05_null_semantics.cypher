// @id: F-05
// @title: NULL: missing data is not false
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: A missing property evaluates to null, comparisons with null yield null (not false), WHERE keeps only true, and
//   NOT null is still null - so rows with missing values vanish from both a condition and its negation.
// @biopharma: Real GxP data always has gaps (yield not yet calculated, disposition pending). Reports that silently drop the
//   gaps under-state populations; this is a data-integrity issue, not just a syntax one.
// @expect: One row: batches 29, withYield 26, above70 17, notAbove70 9, missing 3, notAbove70IncludingNulls 12. Note 17 + 9
//   = 26, not 29.
// @pitfall: WHERE x > 70 and WHERE NOT x > 70 together miss every row where x is null. Test with IS NULL / IS NOT NULL,
//   never = null, and use coalesce(x, default) when a default is legitimate.
// @docs: Cypher manual: Working with null; Functions > Scalar functions (coalesce).
// ---
MATCH (b:Batch)
RETURN count(*)                                                    AS batches,
       count(b.overallYieldPct)                                    AS withYield,
       count(CASE WHEN b.overallYieldPct > 70 THEN 1 END)          AS above70,
       count(CASE WHEN NOT b.overallYieldPct > 70 THEN 1 END)      AS notAbove70,
       count(CASE WHEN b.overallYieldPct IS NULL THEN 1 END)       AS missing,
       count(CASE WHEN coalesce(b.overallYieldPct, 0) <= 70 THEN 1 END) AS notAbove70IncludingNulls;
