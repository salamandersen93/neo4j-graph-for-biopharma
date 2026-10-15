// @id: F-15
// @title: UNION and UNION ALL
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: UNION removes duplicate rows across the combined queries, UNION ALL keeps them; the column names and count must
//   match in every arm.
// @biopharma: Governance checks (see TRV-05) are written as one query per rule joined with UNION; knowing which form de-
//   duplicates avoids hiding repeated findings or double-counting them.
// @expect: Statement 1 (UNION ALL): 3 rows. Statement 2 (UNION): 2 rows, because 'Monoclonal antibody' appears twice.
// @pitfall: UNION without ALL sorts out duplicates, which costs a de-duplication step; if the arms cannot overlap, UNION ALL
//   is the cheaper and correct choice. Mixing UNION and UNION ALL in one query is an error.
// @docs: Cypher manual: Clauses > UNION.
// ---
MATCH (b:Batch {status: 'Rejected'})-[:OF_PRODUCT]->(p:Product) RETURN p.modality AS modality
UNION ALL
MATCH (b:Batch {status: 'Under Investigation'})-[:OF_PRODUCT]->(p:Product) RETURN p.modality AS modality;

MATCH (b:Batch {status: 'Rejected'})-[:OF_PRODUCT]->(p:Product) RETURN p.modality AS modality
UNION
MATCH (b:Batch {status: 'Under Investigation'})-[:OF_PRODUCT]->(p:Product) RETURN p.modality AS modality;
