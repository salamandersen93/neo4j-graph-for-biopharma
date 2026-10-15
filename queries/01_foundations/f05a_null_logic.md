> **Three-valued logic in one table.** Every comparison with `null` returns `null`, and `WHERE` keeps only `true`.
>
> | Expression | Result |
> |---|---|
> | `null = null` | `null` (not true) |
> | `null IS NULL` | `true` |
> | `NOT null` | `null` |
> | `true AND null` | `null` |
> | `false AND null` | `false` |
> | `true OR null` | `true` |
> | `null IN [1, 2]` | `null` |
> | `coalesce(null, 0)` | `0` |
>
> In a regulated data set this is a data-integrity point as much as a syntax one: a missing value is not a pass and
> not a fail, and a filter that does not decide which it is will drop the record without telling anyone.
