// @id: Q09
// @title: Variable-length path: reconstruct an ordered recipe
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: -[:FOLLOWED_BY*]-> walks any number of hops; NOT (last)-[:FOLLOWED_BY]->() finds the end of the
//   chain; list comprehensions reshape nodes(path).
// @biopharma: A purification process is an ordered sequence of unit operations defined in a controlled document.
//   Reading it back from the data confirms that the electronic recipe matches the approved document
//   (recipe verification).
// @expect: One row: 8 steps joined in order (7 hops), from harvest clarification to final filtration and bulk
//   fill.
// ---
MATCH (:PurificationProtocol {protocolId:'SOP-DSP-0101-v2.0'})-[:INCLUDES]->(first:PurificationStep {stepNumber:1})
MATCH path = (first)-[:FOLLOWED_BY*]->(last:PurificationStep)
WHERE NOT (last)-[:FOLLOWED_BY]->()
RETURN [n IN nodes(path) | toString(n.stepNumber) + '. ' + n.stepName] AS sequence, length(path) AS hops;
