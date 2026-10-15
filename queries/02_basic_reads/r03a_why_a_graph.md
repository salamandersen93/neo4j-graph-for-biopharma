> **Why does this data suit a graph?**
> A batch record touches cell banks, a vessel, a recipe, dozens of material lots, samples, results, people and
> deviations. In tables every question is a different multi-way join, and every new question means re-planning the join.
> In a graph the relationships are stored data, so the same traversal that answers "genealogy of one batch" (R-02) also
> answers "every batch that used this resin lot" (TRV-04) by walking the same edges the other way. The trade-off is real:
> wide aggregations over millions of flat rows are usually faster in a columnar engine, which is why production
> architectures often use both (see the note after ANA-05).
