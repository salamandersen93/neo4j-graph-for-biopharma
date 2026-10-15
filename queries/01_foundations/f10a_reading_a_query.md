> **Reading a query for correctness.** Cypher reads top to bottom as a pipeline of stages, and each stage hands a table of
> rows to the next. When you are asked whether a query is right, check in this order:
>
> 1. **What is in scope?** Only variables bound by earlier stages, and after `WITH` only the ones it lists.
> 2. **Where does each `WHERE` attach?** To the `MATCH`, `OPTIONAL MATCH` or `WITH` directly above it - and that decides
>    whether rows are removed or only the optional part is.
> 3. **What does each aggregate ignore?** `null`s, and what are the grouping keys (every other `RETURN`/`WITH` item).
> 4. **What happens to missing data?** Follow a `null` through each condition.
> 5. **What is the row count at each stage?** Joins by pattern multiply rows; aggregation collapses them.
>
> Most wrong answers on both exams and real dashboards come from steps 2 to 4.
