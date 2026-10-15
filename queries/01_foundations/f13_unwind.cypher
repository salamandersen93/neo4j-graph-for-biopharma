// @id: F-13
// @title: UNWIND: lists to rows (and the empty-list trap)
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: UNWIND turns a list into one row per element - the standard way to feed a list of identifiers or parameters into
//   a query; the inverse of collect().
// @biopharma: Investigators receive lists of batch or lot numbers from a complaint or audit finding; UNWIND plus OPTIONAL
//   MATCH both looks them up and shows which identifiers do not exist.
// @expect: Statement 1: three rows, BTX101-24-001 Released, BTX202-24-001 Released, NOT-A-BATCH null. Statement 2: zero
//   rows.
// @pitfall: UNWIND of an empty list (or of null) produces no rows, so everything after it vanishes and the query returns
//   nothing without an error. Wrap in OPTIONAL MATCH or guard with coalesce(list, []) when that matters.
// @docs: Cypher manual: Clauses > UNWIND.
// ---
UNWIND ['BTX101-24-001', 'BTX202-24-001', 'NOT-A-BATCH'] AS batchNumber
OPTIONAL MATCH (b:Batch {batchNumber: batchNumber})
RETURN batchNumber, b.status AS status;

UNWIND [] AS nothing
RETURN 'never returned' AS message;
