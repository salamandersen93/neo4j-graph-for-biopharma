// @id: F-02
// @title: AND, OR, NOT and precedence: parenthesise
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: AND binds tighter than OR (and NOT tighter than AND), exactly as in SQL; mixed conditions without parentheses
//   silently mean something else.
// @biopharma: Disposition queries such as 'rejected or under investigation, at 2000 L' drive escalation lists. A precedence
//   slip changes which batches are in scope without any error.
// @expect: Two rows: 'no parentheses' 2 batches, 'with parentheses' 1 batch. The first form means Rejected (any scale) OR
//   (Under Investigation AND 2000 L).
// @pitfall: XOR also exists (true when exactly one side is true). Cypher uses <> for not-equal; != is not valid.
// @docs: Cypher manual: Predicates > Boolean operators (AND, OR, XOR, NOT) and operator precedence.
// ---
MATCH (b:Batch)
WHERE b.status = 'Rejected' OR b.status = 'Under Investigation' AND b.scaleL = 2000
RETURN 'no parentheses' AS form, count(b) AS batches
UNION ALL
MATCH (b:Batch)
WHERE (b.status = 'Rejected' OR b.status = 'Under Investigation') AND b.scaleL = 2000
RETURN 'with parentheses' AS form, count(b) AS batches;
