// @id: TRV-04
// @title: Forward impact trace: the recall question
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: Start at a flagged node, traverse forward through relationships carrying properties (quantity,
//   unit), and aggregate what you find.
// @biopharma: When a supplier notifies you about a raw-material or resin lot, you must identify every batch of
//   every product made with it, within hours. Forward traceability is a core GMP material-control
//   expectation; this is the query graphs exist for.
// @expect: 6 rows: the batches that consumed lot L24-011-003 (the Protein A resin lot flagged Supplier
//   Notification), all Released, with how many release results each has and how many were OOS.
// ---
MATCH (l:MaterialLot {status:'Supplier Notification'})-[:LOT_OF]->(m:Material)
MATCH (l)<-[c:CONSUMED]-(b:Batch)-[:OF_PRODUCT]->(p:Product)
OPTIONAL MATCH (b)<-[:TAKEN_FROM]-(:Sample {sampleType:'Release'})<-[:ON_SAMPLE]-(t:TestResult {resultStatus:'Valid'})
RETURN m.name AS material, l.lotNumber AS lot, p.productCode AS product, b.batchNumber AS batch,
       b.status AS status, c.quantity + ' ' + c.unit AS used,
       count(t) AS releaseResults, sum(CASE WHEN t.outcome = 'OOS' THEN 1 ELSE 0 END) AS oos
ORDER BY batch;
