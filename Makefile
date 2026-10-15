# biopharma-graph - everything is generated from model/spec.py + src/generate.py + queries/
PY ?= python3 -I
.PHONY: test all build data validate model lint-model cypher queries-check docs importer-zip clean new-query
all: build queries-check docs
build: data validate model lint-model cypher
data:        ; $(PY) src/generate.py data
validate:    ; $(PY) src/validate.py data
model:       ; $(PY) src/build_importer_json.py data data/neo4j_importer_model.json
lint-model:  ; $(PY) src/check_importer_json.py data/neo4j_importer_model.json data
cypher:      ; $(PY) src/make_cypher.py data cypher
queries-check: ; $(PY) tools/queries.py lint
docs:        ; $(PY) tools/queries.py docs
importer-zip: build
	mkdir -p dist && rm -f dist/biopharma_importer.zip && cd data && zip -q ../dist/biopharma_importer.zip *.csv neo4j_importer_model.json
	@echo "dist/biopharma_importer.zip -> upload to Aura > Import"
# make new-query SECTION=04_analytics SLUG=my_query TITLE="My query"
new-query:   ; $(PY) tools/queries.py new "$(SECTION)" "$(SLUG)" "$(TITLE)"
clean:       ; rm -rf dist
test:        ; $(PY) -m unittest discover -s tests -v
