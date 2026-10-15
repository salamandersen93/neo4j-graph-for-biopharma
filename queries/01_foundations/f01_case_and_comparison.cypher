// @id: F-01
// @title: Equality is case-sensitive: toLower and friends
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: String comparison with = is exact and case-sensitive, so a mismatch returns zero rows and no error; normalise
//   with toLower() or toUpper() before comparing.
// @biopharma: Material, method and equipment names come from several systems (ERP, LIMS, QMS) with inconsistent
//   capitalisation. Matching them safely is the first step of any cross-system lookup.
// @expect: Statement 1 returns one row: exactMatch 0, lowerMatch 1. Statement 2 returns the single material 'CHO Production
//   Basal Medium'.
// @pitfall: Wrapping a property in a function such as toLower() usually stops a regular (range) index from being used, so on
//   large data you pay for a scan; the usual fixes are a text index or storing a normalised copy of the property.
// @docs: Cypher manual: Functions > String functions (toLower, toUpper); Operators > Comparison operators.
// ---
MATCH (m:Material)
RETURN count(CASE WHEN m.name = 'cho production basal medium' THEN 1 END)          AS exactMatch,
       count(CASE WHEN toLower(m.name) = 'cho production basal medium' THEN 1 END) AS lowerMatch;

MATCH (m:Material)
WHERE toLower(m.name) = 'cho production basal medium'
RETURN m.name AS name;
