// @id: ANA-04
// @title: Relationship-property math: medium per gram of product
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: Facts such as quantity and unit live on the CONSUMED relationship, so aggregate over r.property
//   directly.
// @biopharma: Material consumption per gram of drug substance feeds cost-of-goods and process-efficiency metrics
//   (for example process mass intensity).
// @expect: One row per product, ordered by liters of medium per gram.
// ---
MATCH (p:Product)<-[:OF_PRODUCT]-(b:Batch)-[c:CONSUMED]->(:MaterialLot)-[:LOT_OF]->(:Material {name:'CHO Production Basal Medium'})
WHERE b.drugSubstanceG IS NOT NULL
RETURN p.productCode AS product, count(b) AS batches,
       round(sum(c.quantity) / sum(b.drugSubstanceG), 2) AS mediumLitersPerGramDS
ORDER BY mediumLitersPerGramDS;
