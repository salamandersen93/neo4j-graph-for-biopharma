> **Queries as controls (ALCOA+).**
> Data-integrity expectations are usually summarised as ALCOA+: records are *Attributable, Legible, Contemporaneous,
> Original, Accurate*, plus *Complete, Consistent, Enduring, Available*. Several map onto this model directly:
> `PERFORMED_BY` / `REVIEWED_BY` (attributable), `testedAt` / `reviewedAt` (contemporaneous), deviations and retests that
> are *added* instead of overwriting results (original, enduring), the reconciliation counts in O-02 (complete).
> TRV-05 shows the pattern: express a rule as a query, run it on a schedule, and treat every returned row as an event to
> investigate. This is a teaching dataset, not a validated system, and nothing here is regulatory advice.
