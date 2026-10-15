// @id: Q19
// @title: Let a constraint reject you
// @level: beginner
// @neo4j: 5.x
// @writes: true
// @learn: CREATE always inserts; the uniqueness constraint is the only thing stopping a duplicate. Its backing
//   index is also what makes MERGE fast.
// @biopharma: Unique identification of records is a basic data-integrity expectation. The same error that blocks a
//   duplicate lab ID blocks a duplicate batch number, and it is the error class you met during the
//   original import.
// @expect: The CREATE fails with a ConstraintValidationFailed error naming labId = QC-MICRO. SHOW CONSTRAINTS
//   then lists the constraint on Lab.
// @undo: none: the CREATE is rejected by the constraint, so nothing is written.
// @expect-error: true
// ---
CREATE (:Lab {labId:'QC-MICRO', name:'Duplicate on purpose'});
SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties WHERE 'Lab' IN labelsOrTypes;
