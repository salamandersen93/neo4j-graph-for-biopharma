// @id: F-06
// @title: Label expressions: OR, NOT and AND on labels
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: A node pattern can match several labels at once with | (either), & (both), ! (not) and parentheses; WHERE
//   n:Label tests a label on an already-bound node.
// @biopharma: Cross-entity searches ('every Batch or CellBank touched by this event') are routine in impact assessment; label
//   expressions avoid UNION-ing near-identical queries.
// @expect: Statement 1: two rows, [Batch] 29 and [CellBank] 11. Statement 2: one row, everythingElse 1099 (1262 nodes minus
//   29 batches and 134 samples).
// @pitfall: n:!Batch&!Sample means neither label; n:!(Batch&Sample) means not-both, which is almost every node. Label
//   expressions in MATCH and WHERE are 5.x syntax; Neo4j 4.x had only a single label per pattern element.
// @docs: Cypher manual: Patterns > Label expressions.
// ---
MATCH (n:Batch|CellBank)
RETURN labels(n) AS labels, count(*) AS nodes
ORDER BY nodes DESC;

MATCH (n:!Batch&!Sample)
RETURN count(n) AS everythingElse;
