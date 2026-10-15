// @id: Q15
// @title: Durations from temporal properties
// @level: intermediate
// @neo4j: 5.x
// @writes: false
// @learn: datetime properties are real temporal types: duration.between(a, b).days works, and date(x).year
//   etc. are available for roll-ups.
// @biopharma: Culture duration and hold times are capacity-planning inputs and leading indicators of process
//   drift.
// @expect: 4 rows (50, 200, 500 and 2000 L), runs ordered by scale, with roughly 12-16 day cultures.
// ---
MATCH (br:Bioreactor)-[r:PRODUCES]->(:Batch)
WHERE r.endTime IS NOT NULL
WITH br.nominalVolumeL AS scaleL, duration.between(r.startTime, r.endTime) AS d
RETURN scaleL, count(*) AS runs, round(avg(d.days),1) AS avgCultureDays, min(d.days) AS minDays, max(d.days) AS maxDays
ORDER BY scaleL;
