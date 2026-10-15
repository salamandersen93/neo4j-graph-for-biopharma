// @id: Q21
// @title: Versioned supersede in one transaction
// @level: advanced
// @neo4j: 5.x
// @writes: true
// @learn: One statement is one atomic transaction; the status filter in the MATCH makes a second run a no-op,
//   and the unique protocolId constraint backs that up.
// @biopharma: A controlled document has exactly one effective version at a time, with no gap and no overlap;
//   revising it must be atomic. The SUPERSEDES chain keeps the full history that an audit trail needs.
// @expect: First run: one row (v2.0 Superseded, v3.0 Effective). Second run: no rows. v3.0 is a stub with no
//   steps, which is why the undo exists. Remove anything you attach to v3.0 before running the undo, or
//   it is left orphaned.
// @undo: MATCH (new:PurificationProtocol {protocolId:'SOP-DSP-0101-v3.0'})-[:SUPERSEDES]->(old)
// SET old.status='Effective', old.supersededDate=null
// DETACH DELETE new;
// ---
MATCH (old:PurificationProtocol {protocolId:'SOP-DSP-0101-v2.0', status:'Effective'})
CREATE (new:PurificationProtocol {protocolId:'SOP-DSP-0101-v3.0', documentNumber:old.documentNumber, name:old.name,
        version:'3.0', status:'Effective', effectiveDate:datetime('2026-11-01T00:00:00Z'), description:'Training exercise'})
CREATE (new)-[:SUPERSEDES]->(old)
SET old.status='Superseded', old.supersededDate=new.effectiveDate
RETURN old.protocolId, old.status, new.protocolId, new.status;
