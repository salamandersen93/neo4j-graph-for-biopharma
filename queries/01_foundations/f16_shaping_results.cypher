// @id: F-16
// @title: Shaping results: aliases, DISTINCT, map projection, missing keys
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: RETURN can alias, de-duplicate with DISTINCT, and build maps with projection (b {.a, .b}); reading a property
//   that does not exist returns null instead of an error.
// @biopharma: Result shapes matter when queries feed dashboards or APIs: projecting only the fields a consumer needs keeps
//   payloads small and avoids exposing attributes by accident.
// @expect: Statement 1: one row with summary {batchNumber, status, scaleL}, propertyCount 9, missing null. Statement 2: six
//   distinct statuses.
// @pitfall: A misspelled property name is not an error - it is null, so the typo shows up as an empty column or a vanished
//   filter result. Check names against the model (docs/MODEL.md) or SHOW/db.schema output when a result is
//   unexpectedly empty.
// @docs: Cypher manual: Clauses > RETURN; Expressions > Map expressions (map projection).
// ---
MATCH (b:Batch {batchNumber: 'BTX101-24-001'})
RETURN b {.batchNumber, .status, .scaleL} AS summary,
       size(keys(b))                       AS propertyCount,
       b.noSuchProperty                    AS missing;

MATCH (b:Batch)
RETURN DISTINCT b.status AS status
ORDER BY status;
