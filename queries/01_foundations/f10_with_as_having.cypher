// @id: F-10
// @title: WITH as pipeline and HAVING
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: WITH ends one query stage and starts the next: only what it lists stays in scope, and a WHERE after WITH filters
//   aggregated values - Cypher's HAVING.
// @biopharma: Screening populations ('products with at least five lots to date') before a statistical comparison avoids
//   drawing conclusions from two or three runs.
// @expect: Three rows: BTX-101 (8 batches, 6 released), BTX-505 (7, 6), BTX-202 (6, 5).
// @pitfall: Aggregates are not allowed in WHERE after MATCH (WHERE count(b) >= 5 is an error); aggregate in WITH, then
//   filter. Any variable not listed in WITH is gone afterwards.
// @docs: Cypher manual: Clauses > WITH.
// ---
MATCH (p:Product)<-[:OF_PRODUCT]-(b:Batch)
WITH p, count(b) AS batches, count(CASE WHEN b.status = 'Released' THEN 1 END) AS released
WHERE batches >= 5
RETURN p.productCode AS product, batches, released
ORDER BY batches DESC;
