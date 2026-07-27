# P12 — knowledge-ingestion

**Tier:** Pedagogy
**Code location:** `services/api/app/knowledge/ingestion/`
**Milestone:** 4
**Status:** not started

## Purpose

The pipeline that turns curated sources into a searchable corpus: fetch,
normalise, chunk, embed, and index into Data Connect's vector search. Runs
offline on a schedule — never on the request path — and owns corpus versioning so
`B10` can invalidate cached courses when the knowledge behind them changes.

## Scope

**Owns**
- Fetch and normalisation per source
- Chunking strategy and chunk metadata
- Embedding generation
- Indexing into vector search
- Corpus versioning
- Refresh scheduling and staleness detection
- Ingestion cost accounting into `F07`

**Does not own**
- Which sources → `P11`
- Retrieval → `P13`
- Vector store provisioning → `F03`
- Corpus table definitions → `F01`

## Source references

- `ARCHITECTURE.md` § "Auth + Database" — Data Connect provides vector search
  (lines 55–56)
- `ARCHITECTURE.md` § "AI compute — Cloud Run" — containerised Python service
  (lines 74–82)
- `FEATURE_PLAN.md` § 2 "Cost control & reuse" (lines 83–85)

## Depends on

`P11`, `F01` (corpus tables), `F03` (vector search, embedding model access), `B03`

*(Offline pipeline: this module runs on a schedule and calls the shared Vertex
client for embeddings, so like `P17` it is a documented exception to the rule that
Tier P does not depend on Tier B. `P13`, which sits on the request path, is not
exempt and has no backend dependency.)*

## Depended on by

`P13`, `B10` (corpus version in the cache key)

## Decisions inherited

**Divergence from `ARCHITECTURE.md`, recorded deliberately.**
`ARCHITECTURE.md:55-56` states that vector search availability "is a bonus for
later (semantic review, RAG over course content) without adding another
datastore." Choosing retrieval grounding for v1 promotes that from later to now.

This is **not** an architecture violation — Data Connect already provides the
vector store, so the "no second datastore" commitment holds. What it adds is this
ingestion pipeline, corpus tables in `F01`, embedding spend in `F07`, and a
retrieval hop in `P13`.

Per the project's drift convention, `ARCHITECTURE.md` stays frozen as the original
decision record and this spec carries the change. See also `P13`.

## Pipeline

```
source (P11) ──fetch──▶ normalise ──chunk──▶ embed ──▶ index (vector search)
                                                          │
                                              corpus_version bumped
                                                          │
                                                   B10 invalidates
```

## Chunking

Chunk boundaries follow the document's own structure — headings, sections, code
blocks — rather than a fixed token count. Fixed-size chunking splits a code
example from its explanation and a claim from its qualifier, which is precisely
the material that must stay together for grounding to be useful.

Every chunk carries metadata that `P13` filters on and `P14` cites: source id,
trust tier, document URL, section path, and the version or retrieval date the
content reflects.

## Corpus versioning

The corpus has a version that increments when content changes. `B10`'s cache key
includes it alongside the `P10` prompt version, so a course generated against
superseded knowledge is invalidated rather than served indefinitely.

Granularity is an open question below — a global version is simple but invalidates
everything on any change.

## Refresh and staleness

Each source's cadence from `P11` drives re-fetch. On change: re-chunk, re-embed,
bump the version. A source that fails to fetch repeatedly is flagged rather than
silently serving stale content — stale grounding is the failure mode this whole
area exists to prevent.

## Open questions

- Corpus version granularity: global, per source, or per topic domain. Per source
  is the likely right answer but requires `B10` to track which sources a course
  drew on, which means persisting retrieval provenance.
- Embedding model choice and dimensionality, and the cost of re-embedding the
  whole corpus if it changes.
- Where the job runs. Cloud Run scales to zero, so this needs either a scheduled
  invocation or a separate job runtime — the same open question `B18` has.
- Whether code blocks should be embedded at all, or indexed separately, given
  code and prose embed very differently.
- Initial corpus size, and whether ingestion cost is a one-off or ongoing concern.

## Acceptance criteria

- [ ] A curated source is fetched, chunked, embedded, and retrievable end to end
- [ ] Chunks respect document structure — no chunk splits a code block from its
      explanation
- [ ] Every chunk carries source, tier, URL, section, and version metadata
- [ ] A source change bumps the corpus version and invalidates the right `B10`
      entries
- [ ] A failing source is flagged rather than serving stale content silently
- [ ] Ingestion never runs on the request path
- [ ] Embedding spend appears in `F07` as its own category
