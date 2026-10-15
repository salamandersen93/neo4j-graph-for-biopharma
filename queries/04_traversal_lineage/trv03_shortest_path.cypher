// @id: TRV-03
// @title: Shortest path (always bound it)
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: shortestPath() finds the fewest-hop route; the [*..5] bound is what keeps it safe on a dense graph.
// @biopharma: Investigations trace a result back to the equipment and batch that produced it. Bounded traversals
//   are cheap; an unbounded variable-length search over a connected manufacturing graph can touch most
//   of the database.
// @expect: One row: 3 hops (TestResult -> Sample -> Batch <- Bioreactor). Run EXPLAIN and find the
//   CartesianProduct operator.
// ---
MATCH (t:TestResult {resultId:'R-000001'}), (br:Bioreactor)
MATCH p = shortestPath((t)-[*..5]-(br))
RETURN br.equipmentId AS bioreactor, length(p) AS hops, [n IN nodes(p) | labels(n)[0]] AS route
ORDER BY hops LIMIT 1;
