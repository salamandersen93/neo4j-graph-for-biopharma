// @id: R-03
// @title: Implicit grouping: yield by product and scale
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: Every non-aggregated column in RETURN becomes a grouping key; there is no GROUP BY clause.
// @biopharma: Comparing titer and downstream yield across scales is basic process-development analytics, and the
//   starting point of a scale-up or comparability discussion (ICH Q11, ICH Q5E).
// @expect: One row per product and scale combination that has completed batches.
// ---
MATCH (p:Product)<-[:OF_PRODUCT]-(b:Batch)
WHERE b.overallYieldPct IS NOT NULL
RETURN p.productCode AS product, b.scaleL AS scaleL, count(b) AS batches,
       round(avg(b.titerGPerL),2) AS avgTiter, round(avg(b.overallYieldPct),1) AS avgYield
ORDER BY product, scaleL;
