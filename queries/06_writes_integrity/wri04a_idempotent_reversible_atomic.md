> **Three words that get confused.**
>
> | Property | Meaning | Example here |
> |---|---|---|
> | **Idempotent** | Running it twice leaves the same state as running it once | WRI-02 (`MERGE` on the key) |
> | **Atomic** | It fully happens or does not happen at all | WRI-03 (one statement, one transaction) |
> | **Reversible** | You can get back to the previous state | The `@undo` blocks, which exist only for scratch data |
>
> Idempotency says nothing about whether the *first* run should have happened. WRI-02 cannot create a duplicate, but its
> first run still leaves an open deviation on a released batch.
