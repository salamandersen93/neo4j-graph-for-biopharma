// @id: F-09
// @title: count(*), count(x), count(DISTINCT x) and null-skipping aggregates
// @level: beginner
// @neo4j: 5.x
// @writes: false
// @exam: cypher
// @learn: count(*) counts rows, count(x) counts non-null values, DISTINCT de-duplicates, and avg/sum/min/max ignore nulls
//   - so avg is not sum divided by the row count.
// @biopharma: A mean yield over 'all batches' that quietly excludes batches without a yield is a different statement from the
//   mean over every batch; continued process verification needs to say which one it reports.
// @expect: One row: rows 29, nonNull 26, statuses 6, avgIgnoresNull 71.4, sumOverAllRows 64.0, firstDisposition 2024-09-02,
//   statusList containing the six statuses (order not guaranteed).
// @pitfall: collect() also skips nulls. An aggregate with no grouping key returns exactly one row even on empty input (count
//   0, others null), unlike a grouped aggregate, which returns no rows.
// @docs: Cypher manual: Functions > Aggregating functions.
// ---
MATCH (b:Batch)
RETURN count(*)                                   AS rows,
       count(b.overallYieldPct)                   AS nonNull,
       count(DISTINCT b.status)                   AS statuses,
       round(avg(b.overallYieldPct), 1)           AS avgIgnoresNull,
       round(sum(b.overallYieldPct) / count(*), 1) AS sumOverAllRows,
       min(b.dispositionDate)                     AS firstDisposition,
       collect(DISTINCT b.status)                 AS statusList;
