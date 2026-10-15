// @id: F-07
// @title: Patterns as predicates: (a)-[]->() and EXISTS { }
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: A relationship pattern in WHERE is a true/false test on graph shape; when you need to filter the node at the
//   other end, use EXISTS { MATCH ... WHERE ... }.
// @biopharma: 'Which released batches have no deviation?' and 'which batches are touched by an open deviation?' are the basic
//   questions a QA review asks before certification.
// @expect: Statement 1: 8. Statement 2: 21. Statement 3: two rows, BTX101-26-002 and BTX404-26-001.
// @pitfall: A pattern predicate may not introduce a new variable: WHERE (b)<-[:AFFECTS]-(d:Deviation {status:'Open'}) is
//   rejected. Use EXISTS { (b)<-[:AFFECTS]-(d:Deviation) WHERE d.status = 'Open' } instead.
// @docs: Cypher manual: Subqueries > EXISTS subqueries; Predicates > Path pattern expressions.
// ---
MATCH (b:Batch)
WHERE (b)<-[:AFFECTS]-(:Deviation)
RETURN count(b) AS batchesWithDeviation;

MATCH (b:Batch)
WHERE NOT (b)<-[:AFFECTS]-(:Deviation)
RETURN count(b) AS batchesWithoutDeviation;

MATCH (b:Batch)
WHERE EXISTS { (b)<-[:AFFECTS]-(d:Deviation) WHERE d.status = 'Open' }
RETURN b.batchNumber AS batch, b.status AS status
ORDER BY batch;
