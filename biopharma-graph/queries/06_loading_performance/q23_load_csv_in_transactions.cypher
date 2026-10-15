// @id: Q23
// @title: LOAD CSV in batched transactions
// @level: advanced
// @neo4j: 5.23+
// @writes: true
// @learn: Everything in a CSV is a string until converted; create constraints first, MERGE on the key, and
//   batch with IN TRANSACTIONS.
// @biopharma: This is how scripted pipelines land data so a re-run is safe. The Importer is for one-off loads and
//   model prototyping; anything that runs on a schedule should be code in a repository with tests.
// @expect: Does not run as written: it needs the CSV hosted at a public URL. Replace the placeholder; you may
//   need the :auto prefix in some clients.
// @undo: none: MERGE on existing keys rewrites the same values when the CSV matches the loaded data.
// @skip-run: needs a publicly hosted CSV
// ---
LOAD CSV WITH HEADERS FROM 'https://<your-public-url>/test_results.csv' AS row
CALL (row) {
  MERGE (t:TestResult {resultId: row.resultId})
  SET t.attempt = toInteger(row.attempt), t.value = toFloat(row.value), t.testedAt = datetime(row.testedAt)
} IN TRANSACTIONS OF 500 ROWS;
