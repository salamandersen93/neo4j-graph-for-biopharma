// @id: F-04
// @title: STARTS WITH, CONTAINS, ENDS WITH and regular expressions
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: There is no LIKE: use STARTS WITH, ENDS WITH and CONTAINS for simple matching, and =~ for a regular expression
//   that must match the whole string.
// @biopharma: Free-text fields such as material names, deviation titles and root causes are searched constantly during
//   investigations ('everything mentioning Resin').
// @expect: One row: startsWithCHO 2, containsResin 4, endsWithMedium 2, regexNoWildcard 0, regexWithWildcard 2,
//   regexCaseInsensitive 4.
// @pitfall: =~ is anchored: m.name =~ 'CHO' is false for 'CHO Feed Medium' because the pattern must match the entire value.
//   Use '.*CHO.*' for 'contains', and the (?i) flag for case-insensitive matching. There is no % wildcard.
// @docs: Cypher manual: Predicates > String operators; Operators > Regular expressions.
// ---
MATCH (m:Material)
RETURN count(CASE WHEN m.name STARTS WITH 'CHO'    THEN 1 END) AS startsWithCHO,
       count(CASE WHEN m.name CONTAINS 'Resin'     THEN 1 END) AS containsResin,
       count(CASE WHEN m.name ENDS WITH 'Medium'   THEN 1 END) AS endsWithMedium,
       count(CASE WHEN m.name =~ 'CHO'             THEN 1 END) AS regexNoWildcard,
       count(CASE WHEN m.name =~ '.*CHO.*'         THEN 1 END) AS regexWithWildcard,
       count(CASE WHEN m.name =~ '(?i).*resin.*'   THEN 1 END) AS regexCaseInsensitive;
