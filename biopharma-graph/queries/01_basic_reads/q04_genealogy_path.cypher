// @id: Q04
// @title: Bind and return a path (cell bank genealogy)
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: Assigning a pattern to a variable (path = ...) lets you return the whole route; switch the result to
//   graph view to see it.
// @biopharma: Cell-substrate history (master bank, working bank, production batch) is the root of traceability for
//   a biologic. Regulators expect every lot to be traceable to its cell bank (see ICH Q5D on cell
//   substrates).
// @expect: One path: batch -> working cell bank -> master cell bank -> product.
// ---
MATCH path = (:Batch {batchNumber:'BTX101-24-001'})-[:INOCULATED_FROM]->(:CellBank)
             -[:DERIVED_FROM]->(:CellBank)-[:EXPRESSES]->(:Product)
RETURN path;
