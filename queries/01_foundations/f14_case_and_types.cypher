// @id: F-14
// @title: CASE, integer division and type conversion
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: CASE is an expression (generic or simple form), / on two integers is integer division, ^ always returns a float,
//   and toInteger()/toFloat() return null rather than failing on text that cannot convert.
// @biopharma: Unit and scale arithmetic (volumes, ratios, yields) goes wrong quietly when integer division truncates, and
//   imported CSV text must be converted explicitly.
// @expect: Statement 1: intDivision 2, floatDivision 2.5, modulo 1, power 8.0, parsed 13, parsedFloat 3.5, badParse null.
//   Statement 2: production 11, pilot 10, development 8. Statement 3: Released 22.
// @pitfall: 5 / 2 is 2, not 2.5; make one operand a float. LOAD CSV delivers everything as strings, so numeric and date
//   columns need toInteger(), toFloat() or datetime() before comparing or doing arithmetic.
// @docs: Cypher manual: Expressions > CASE; Operators > Mathematical operators; Functions > Scalar functions.
// ---
RETURN 5 / 2 AS intDivision, 5 / 2.0 AS floatDivision, 5 % 2 AS modulo, 2 ^ 3 AS power,
       toInteger('12') + 1 AS parsed, toFloat('3.5') AS parsedFloat, toInteger('abc') AS badParse;

MATCH (b:Batch)
RETURN CASE WHEN b.scaleL >= 2000 THEN 'production'
            WHEN b.scaleL >= 500  THEN 'pilot'
            ELSE 'development' END AS scaleClass,
       count(*) AS batches
ORDER BY batches DESC;

MATCH (b:Batch)
RETURN b.status AS status,
       CASE b.status WHEN 'Released' THEN 'final' WHEN 'Rejected' THEN 'final' ELSE 'open' END AS stage,
       count(*) AS batches
ORDER BY batches DESC LIMIT 1;
