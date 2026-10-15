// @id: Q13
// @title: Governance assertions (every row is a violation)
// @level: advanced
// @neo4j: 5.x
// @writes: false
// @learn: UNION of independent rule checks, each returning (violation, entity); NOT EXISTS {} expresses a
//   missing relationship.
// @biopharma: Data-integrity rules written as executable checks: a released batch must have a QA approver, must
//   not carry a valid OOS result, and second-person review must be independent of the performer. Running
//   these on a schedule is how a data product demonstrates it is under control (in the spirit of 21 CFR
//   Part 11 and the ALCOA+ principles).
// @expect: 0 rows. Any row is a violation that needs a deviation.
// ---
MATCH (b:Batch {status:'Released'})
WHERE NOT EXISTS { (b)<-[:RESPONSIBLE_FOR {role:'QA Approver'}]-(:Employee) }
RETURN 'released without QA approver' AS violation, b.batchNumber AS entity
UNION
MATCH (b:Batch {status:'Released'})<-[:TAKEN_FROM]-(:Sample)<-[:ON_SAMPLE]-(:TestResult {outcome:'OOS', resultStatus:'Valid'})
RETURN 'released with valid OOS' AS violation, b.batchNumber AS entity
UNION
MATCH (a:Employee)<-[:PERFORMED_BY]-(t:TestResult)-[:REVIEWED_BY]->(a)
RETURN 'self-reviewed result' AS violation, t.resultId AS entity;
