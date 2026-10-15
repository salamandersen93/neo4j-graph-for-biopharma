> **Where Cypher stops, and what to pair it with.**
> Graph traversal and relationship-heavy questions belong in Neo4j; large flat aggregations, ML feature engineering
> and heavy statistics usually belong in a lakehouse engine (Spark / SQL on Databricks). The usual production shape is both:
> the graph holds the connected, governed entities and lineage; the lakehouse holds the wide tables; and the two
> exchange data in batches (Neo4j has a Spark connector for this; check its current version and Aura compatibility
> before designing around it). Part of designing a data product is deciding which question goes where.
