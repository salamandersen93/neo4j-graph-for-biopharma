// @id: SUB-03
// @title: Top-N per group with a scoped CALL
// @level: advanced
// @neo4j: 5.23+ (older: CALL { WITH p ... })
// @writes: false
// @learn: CALL (p) { ... LIMIT 2 } runs the LIMIT once per product; a plain LIMIT would cut the whole result.
// @biopharma: Continued process verification looks at the most recent few batches of each product, not the global
//   latest N. Per-group top-N is a pattern you will need constantly.
// @expect: Up to 2 rows per product (10 rows).
// ---
MATCH (p:Product)
CALL (p) {
  MATCH (p)<-[:OF_PRODUCT]-(b:Batch)<-[r:PRODUCES]-(:Bioreactor)
  RETURN b, r.startTime AS started
  ORDER BY started DESC LIMIT 2
}
RETURN p.productCode, b.batchNumber, b.status, started
ORDER BY p.productCode, started DESC;
