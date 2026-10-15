// @id: Q20
// @title: Idempotent upsert with MERGE
// @level: intermediate
// @neo4j: 5.x
// @writes: true
// @learn: MERGE finds-or-creates on the whole pattern; merge on the key only, put everything else in ON CREATE
//   / ON MATCH SET.
// @biopharma: Pipelines must be safe to re-run: the nightly LIMS sync must never create a second copy of a
//   deviation. Merging on identity and setting attributes separately is the standard way to get that.
// @expect: One Deviation (DEV-TEST-001) linked to the batch; run it twice and the count stays at one, with
//   lastTouched set on the second run. Afterwards the batch is Released with an Open deviation, which
//   breaks the rule in Q13-style checks.
// @undo: MATCH (d:Deviation {deviationId:'DEV-TEST-001'}) DETACH DELETE d;
// ---
MATCH (b:Batch {batchNumber:'BTX101-24-001'})
MERGE (d:Deviation {deviationId:'DEV-TEST-001'})
  ON CREATE SET d.deviationType='Process Deviation', d.title='Training exercise', d.severity='Minor',
                d.status='Open', d.openedDate=datetime()
  ON MATCH  SET d.lastTouched=datetime()
MERGE (d)-[:AFFECTS]->(b)
RETURN d, b;
