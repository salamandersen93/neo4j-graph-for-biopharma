// @id: ANA-03
// @title: Statistics and process capability
// @level: advanced
// @neo4j: 5.x
// @writes: false
// @learn: stDev() and percentileCont() are built-in aggregates; a one-sided capability index can be computed
//   against the limit stored in the graph.
// @biopharma: Capability against specification limits is routine in continued process verification and in setting
//   specifications for biotechnological products (ICH Q6B). Conventionally an index below about 1.33
//   draws attention. Caveat: it assumes enough batches and roughly normal data; with a handful of
//   batches per product treat it as a screening number.
// @expect: One row per product, ordered by ppkUpper ascending (lowest capability first).
// ---
MATCH (t:TestResult {resultStatus:'Valid'})-[:AGAINST_SPEC]->(s:Specification {attribute:'High Molecular Weight Species', stage:'Release'})-[:APPLIES_TO]->(p:Product)
WITH p.productCode AS product, s.upperLimit AS usl, count(t) AS n,
     avg(t.value) AS mean, stDev(t.value) AS sd, percentileCont(t.value, 0.95) AS p95
RETURN product, n, round(mean,2) AS mean, round(sd,2) AS sd, round(p95,2) AS p95, usl,
       CASE WHEN sd > 0 THEN round((usl - mean) / (3 * sd), 2) END AS ppkUpper
ORDER BY ppkUpper;
