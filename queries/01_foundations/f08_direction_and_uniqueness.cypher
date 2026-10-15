// @id: F-08
// @title: Direction and relationship uniqueness
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: An undirected pattern matches each relationship in both orientations, and within one MATCH a relationship is
//   never used twice (nodes can repeat, relationships cannot).
// @biopharma: Cell bank genealogy (MCB to WCB) is a regulatory expectation; counting lineage edges wrongly gives a wrong
//   answer on how many working banks derive from a master bank.
// @expect: Statement 1: 6. Statement 2: 12. Statement 3: 2 (the two working banks derived from MCB-BTX101, in both orders).
// @pitfall: Leaving the arrow off doubles the row count when both ends are unbound. Within one MATCH pattern nodes may repeat but a
//   relationship may not, so a path never walks the same edge back; across separate MATCH clauses relationships can repeat.
// @docs: Cypher manual: Patterns > Match modes (relationship uniqueness / DIFFERENT RELATIONSHIPS).
// ---
MATCH (:CellBank)-[:DERIVED_FROM]->(:CellBank)
RETURN count(*) AS directed;

MATCH (:CellBank)-[:DERIVED_FROM]-(:CellBank)
RETURN count(*) AS undirected;

MATCH (a:CellBank)-[:DERIVED_FROM]-(m:CellBank)-[:DERIVED_FROM]-(c:CellBank)
RETURN count(*) AS twoHopsNoRepeatedRelationship;
