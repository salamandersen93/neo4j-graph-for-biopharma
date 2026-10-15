// @id: Q01
// @title: Orient yourself: schema and constraints
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @learn: db.schema.visualization() draws the as-built model; SHOW CONSTRAINTS lists the integrity rules the
//   database enforces.
// @biopharma: Auditors and new team members ask "what do you store and how is it linked?". The as-built schema is
//   the honest answer, as opposed to the as-designed diagram in a slide. Constraints are the first-line
//   data-integrity controls: they are what stops a duplicate batch number or lab ID from existing at
//   all.
// @expect: A graph of 17 labels and 34 relationship types. SHOW CONSTRAINTS returns 18 uniqueness constraints
//   (one per key plus Employee.email).
// ---
CALL db.schema.visualization();
SHOW CONSTRAINTS;
