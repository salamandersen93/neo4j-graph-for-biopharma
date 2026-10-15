// @id: LOD-02
// @title: Read a query plan with PROFILE
// @level: advanced
// @neo4j: 5.x
// @writes: true
// @learn: PROFILE runs the query and reports operators and db hits: a unique-index seek, a label scan, then an
//   index seek once an index exists.
// @biopharma: Performance is a feature of a data product. A real LIMS holds millions of results, so learn to read
//   plans on a small dataset before the data is a thousand times larger. If you ran
//   cypher/post_load.cypher section C, an outcome index already exists: drop TestResult_outcome_idx
//   first to see the contrast.
// @expect: Plan 1: NodeUniqueIndexSeek. Plan 2: NodeByLabelScan. Plan 3: NodeIndexSeek. With very small data
//   the planner may still choose a scan; compare the db hits.
// @undo: DROP INDEX tr_outcome_probe IF EXISTS;
// ---
PROFILE MATCH (b:Batch {batchNumber:'BTX101-24-001'}) RETURN b;
PROFILE MATCH (t:TestResult {outcome:'OOS'}) RETURN count(t);
CREATE INDEX tr_outcome_probe IF NOT EXISTS FOR (t:TestResult) ON (t.outcome);
PROFILE MATCH (t:TestResult {outcome:'OOS'}) RETURN count(t);
