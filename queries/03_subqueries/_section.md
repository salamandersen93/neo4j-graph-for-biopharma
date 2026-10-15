# 03 - Subqueries and per-row logic

Modern Cypher has subquery expressions (`COUNT {}`, `EXISTS {}`, `COLLECT {}`) and scoped `CALL` blocks.
They avoid the row-multiplication traps of chaining `OPTIONAL MATCH` and make per-group logic readable.

<!-- id-prefix: SUB -->
