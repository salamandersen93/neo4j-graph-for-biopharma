# biopharma-graph

A self-contained teaching graph for **biologics drug-substance manufacturing and QC**, built to learn Neo4j / Cypher on a
domain where graphs earn their keep: genealogy, impact analysis, specifications, deviations and GxP data integrity.

Everything is **synthetic**, **reproducible** and **checked**: one model spec generates the CSVs, the Aura importer file,
a validator and the Cypher helpers, and a library of annotated queries (with the "why this matters in drug development"
written next to each one) renders to a single study document.

```
make all      # regenerate data, validate it, lint the model and queries, render docs/queries.md
make test     # unit tests for the tooling
```
Needs Python 3.9+ and `make`. No third-party packages except `neo4j` for the optional live runner.

## Quick start: load it into Aura

1. `make importer-zip` (or use the committed files in `data/`).
2. Aura console > **Query**: run `cypher/reset.cypher` statement by statement. Step 0 lists and drops any constraint or index already in the database, then the rest clears the data.
3. Aura console > **Import**: open the model with data, upload everything from `dist/biopharma_importer.zip` (all CSVs plus `neo4j_importer_model.json`), run the import.
4. **Query**: run `cypher/post_load.cypher` (count checks, optional NOT NULL constraints, lookup indexes).
5. Work through `docs/queries.md`, or run the whole library: `python3 tools/run_queries.py` (see below).

## Repository layout

```
model/spec.py              THE model: labels, properties, keys, relationships, enums (single source of truth)
model/legacy_v1_names.json constraint/index names from the first (failed) model, used by reset.cypher
src/generate.py            synthetic data generator (seeded, deterministic) -> data/*.csv
src/validate.py            9 schema rules + 21 business rules over the CSVs
src/build_importer_json.py generates data/neo4j_importer_model.json from the spec
src/check_importer_json.py lints the importer file (name collisions, dangling refs, CSV drift)
src/make_cypher.py         generates cypher/reset.cypher and cypher/post_load.cypher
data/                      generated CSVs + importer model (committed so the repo is usable without building)
cypher/                    generated reset / post-load scripts
queries/                   the query library (hand-written; see below)
tools/queries.py           lint, render and scaffold the query library
tools/run_queries.py       run the library against a live Aura / Neo4j instance
docs/MODEL.md              the data model and the decisions behind it
docs/queries.md            GENERATED study document from queries/ (do not edit by hand)
tests/                     unit tests for the tooling
.github/workflows/         ci.yml (every push) and aura-smoke.yml (manual, needs secrets)
```

Generated vs hand-written: edit `model/spec.py`, `src/generate.py` and everything under `queries/` and `docs/MODEL.md`;
never edit `data/`, `cypher/` or `docs/queries.md`. CI fails if the committed copies are stale.

## The query library

Queries live in `queries/<NN_section>/`. Every section is a folder; every query is a file; a few extra files carry the prose
that sits between queries.

```
queries/
  03_traversal_lineage/
    _section.md                       first line '# Title', then the section intro (markdown)
    q09_variable_length_recipe.cypher a query with a header block
    q12_recall_impact_trace.cypher
    q13_governance_assertions.cypher
    q13a_queries_as_controls.md       a note rendered after Q13 and before Q14
```

**Anatomy of a query file**: a comment header of `@field:` lines, a `// ---` separator, then plain Cypher (one or several
statements). Continuation lines are ordinary `//` comments. The file stays directly copy-pasteable into the Aura Query tool.

```cypher
// @id: Q12
// @title: Forward impact trace: the recall question
// @level: intermediate                 beginner | intermediate | advanced
// @neo4j: 5.x                          minimum version if newer than 5.x (optional)
// @writes: false                       true needs an @undo
// @learn: The Cypher concept this teaches.
// @biopharma: Where this question appears in drug development / manufacturing / QC, and why a graph answers it.
//   Continuation lines start with '//' and are joined to the field above.
// @expect: What the result should look like on the loaded dataset.
// @undo: statements that reverse a write query (or 'none: reason')      (writes only)
// @expect-error: true                  query is supposed to fail (e.g. a constraint demo)   (optional)
// @skip-run: reason                    the live runner skips it (e.g. needs a hosted file)   (optional)
// ---
MATCH (l:MaterialLot {status:'Supplier Notification'}) ...
```

### Add a query
```
make new-query SECTION=04_analytics SLUG=my_new_query TITLE="My new query"
```
This creates the next free ID (`Q25`, `Q26`, ...) from a template. Fill in the header, write the Cypher, then `make all`.
IDs are stable identifiers rather than positions: a new query can live in any section and keeps its ID if you reorder files.
Within a section, files are ordered by file name.

### Add a section
Create `queries/07_my_section/` with a `_section.md` (first line `# Title`, then the intro) and add queries to it. Folder
prefixes (`00_`, `01_`, ...) set the order. A numbered gap (`07_`, `15_`) is fine.

### Add commentary between queries
Drop a markdown file named `qNNa_anything.md` into the section: it renders right after query `qNN` and before the next one
(`q05a_why_a_graph.md` follows Q05; use `q05b_` for a second note). Notes are free-form markdown; block quotes work well.

### What `make queries-check` enforces
Required fields present; IDs unique and matching the file name; `@level` valid; every write query has an `@undo`; read-only
queries contain no write keywords; and, the useful one, **every label, relationship type and property key used in a query must
exist in `model/spec.py`**, so a typo or a model change that breaks a query fails the build instead of returning empty results.
It is a static check: it does not prove a query is valid Cypher.

### Run the library against Aura
```
pip install -r requirements.txt
cp .env.example .env          # fill in the credentials Aura gave you; .env is git-ignored
python3 tools/run_queries.py                  # read-only queries
python3 tools/run_queries.py --only Q05,Q07
python3 tools/run_queries.py --allow-writes   # also runs write queries and then their @undo (scratch database only)
python3 tools/run_queries.py --dry-run        # print the statements without connecting
```
Output is one PASS / FAIL / SKIP line per query; exit code 1 on any failure. The runner's logic is unit tested with a fake
driver; **it has not been run against a live database by its author**, so treat the first live run as its own test.

## Rebuilding after a model change
1. Edit `model/spec.py` (schema) and `src/generate.py` (data).
2. `make all`. The validator, importer lint and query lint all run; fix whatever they report.
3. Commit the regenerated `data/`, `cypher/` and `docs/queries.md` with the change.
4. Re-import: `reset.cypher`, then the importer zip.

## CI
`ci.yml` runs on every push: regenerate, validate, lint, unit tests, then `git diff --exit-code` to prove the committed
generated files match the sources. `aura-smoke.yml` is manual: it runs the read-only queries against your Aura instance using
repository secrets (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`). Review who can trigger it and what the credentials can do
before enabling it on a shared repository.

## Caveats
- **Synthetic data.** Specification limits, yields and distributions are plausible, not from any real filing. Products and company are fictional.
- **Teaching material, not validated software.** References to ICH guidelines, FDA guidance, 21 CFR Part 11 and ALCOA+ are pointers for further reading, not compliance advice.
- **Untested against Aura by the author:** the importer file's first load was verified by you; `tools/run_queries.py` and `aura-smoke.yml` have not been run against a live instance.
- Query syntax assumes a current Neo4j 5.x / Aura instance; a few queries need 5.9+ or 5.23+ (noted in their headers).

## Ideas for next sections
Graph Data Science / Graph Analytics on the lot-sharing network; vector search and GraphRAG over deviation text;
role-based access control and read-only roles; a Spark connector exchange with a lakehouse; a PDF build of `docs/queries.md`.
