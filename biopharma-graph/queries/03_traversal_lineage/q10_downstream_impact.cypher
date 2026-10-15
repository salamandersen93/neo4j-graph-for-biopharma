// @id: Q10
// @title: Quantified shorthand: everything downstream of a step
// @level: intermediate
// @neo4j: 5.9+
// @writes: false
// @learn: ->+ means "one or more hops"; it is the modern spelling of *1.. and the building block for impact
//   analysis.
// @biopharma: If Protein A capture changes, which later unit operations (viral inactivation, polishing, viral
//   filtration, formulation) are affected? That is exactly the question change control asks when
//   assessing risk (ICH Q9) under a quality system (ICH Q10).
// @expect: 6 rows: steps 3 to 8 of the BTX-505 v2.0 process.
// ---
MATCH (a:PurificationStep {stepId:'SOP-DSP-0505-v2.0-S02'})-[:FOLLOWED_BY]->+(d:PurificationStep)
RETURN d.stepNumber, d.stepName ORDER BY d.stepNumber;
