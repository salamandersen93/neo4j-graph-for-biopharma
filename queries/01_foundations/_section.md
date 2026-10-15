# 01 - Cypher foundations (SQL to Cypher, with the traps)

The earlier sections use Cypher before they explain it. This section goes back to the building blocks, on the same
biopharma graph, with the specific behaviours that catch people who know SQL: case-sensitive strings, `null` logic,
precedence, `WITH`, `OPTIONAL MATCH`, `UNWIND`, sort order. Every query ends in a **Pitfall**: the plausible wrong
version, and why it fails or quietly returns the wrong answer. Reading for correctness matters as much as writing,
because an open-book test will ask you to judge a query, not only to write one.

| SQL habit | Cypher |
|---|---|
| `FROM a JOIN b ON ...` | the pattern `(a)-[:REL]->(b)` in `MATCH` |
| `WHERE` | `WHERE`, or an inline map `{prop: value}` (equality only) |
| `<>` or `!=` | `<>` only |
| `LIKE 'x%'` / `'%x%'` | `STARTS WITH` / `CONTAINS`; `=~` for a regular expression (matches the whole string) |
| `GROUP BY` | none: non-aggregated `RETURN` items are the grouping key |
| `HAVING` | `WITH ... WHERE` |
| `LEFT JOIN` | `OPTIONAL MATCH` |
| `OFFSET n LIMIT m` | `SKIP n LIMIT m` |
| `CASE WHEN ...` | `CASE WHEN ...` (same) |
| `UNION [ALL]` | `UNION [ALL]` (same) |
| `IS NULL` | `IS NULL` (same; and a missing property is `null`) |
| `SELECT DISTINCT` | `RETURN DISTINCT` |
| row per list element (`unnest`) | `UNWIND` |

Two things to keep in mind throughout. Keywords are not case-sensitive, but labels, relationship types, property
names, variables and string values are. And a typo in a property name is not an error: it is `null`.

<!-- id-prefix: F -->
