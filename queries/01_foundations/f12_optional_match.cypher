// @id: F-12
// @title: OPTIONAL MATCH: the LEFT JOIN, and where its WHERE belongs
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: OPTIONAL MATCH keeps the row and returns null when the pattern is absent; a WHERE attached to it filters the
//   optional part only, never the outer rows.
// @biopharma: 'All batches, with their open deviations if any' is the shape of a batch-record review; an inner join would
//   silently remove the clean batches that QA also needs to see.
// @expect: Statement 1: rows 29, withDeviation 8. Statement 2: rows 29, openDeviations 2. Statement 3: 2.
// @pitfall: Moving the condition from the OPTIONAL MATCH's WHERE into a later WHERE turns the left join into an inner join.
//   count(*) counts rows including null-extended ones; count(d) counts only matches.
// @docs: Cypher manual: Clauses > OPTIONAL MATCH.
// ---
MATCH (b:Batch)
OPTIONAL MATCH (b)<-[:AFFECTS]-(d:Deviation)
RETURN count(*) AS rows, count(d) AS withDeviation;

MATCH (b:Batch)
OPTIONAL MATCH (b)<-[:AFFECTS]-(d:Deviation)
WHERE d.status = 'Open'
RETURN count(*) AS rows, count(d) AS openDeviations;

MATCH (b:Batch)<-[:AFFECTS]-(d:Deviation)
WHERE d.status = 'Open'
RETURN count(*) AS rowsAsInnerJoin;
