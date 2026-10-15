// @id: O-02
// @title: Sanity counts after a load
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: Grouping by labels(n)[0] and type(r) gives per-label and per-relationship-type counts without naming
//   them.
// @biopharma: Reconciling record counts between source and target is the minimum completeness control for any GxP
//   data load (the "Complete" and "Consistent" in ALCOA+). A pipeline that loads without reconciling is
//   not finished.
// @expect: 1,262 nodes and 5,601 relationships in total. Compare each row with the counts in
//   cypher/post_load.cypher.
// ---
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS nodes ORDER BY nodes DESC;
MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS rels ORDER BY rels DESC;
