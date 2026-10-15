# 06 - Writing safely

Reads are forgiving; writes are where data products go wrong. This section covers constraints, idempotent upserts,
atomic versioning and invariant checks. **Every query here changes the graph** except WRI-04, so each has an `@undo`.
The undo statements exist only because this is a scratch copy of synthetic data: in a real regulated system you close
or supersede records, you never delete them (see the note after WRI-04).

<!-- id-prefix: WRI -->
