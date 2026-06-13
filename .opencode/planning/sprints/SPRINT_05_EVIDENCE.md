# Sprint 05: Evidence Service

**Duration:** Days 12-22 | **Goal:** Document ingestion, vector search, reliability scoring

## Tasks

### Day 12-14: Document Parsing + Chunking
- [ ] Implement `DocumentParser` for PDF (PyMuPDF)
- [ ] Implement `DocumentParser` for DOCX (python-docx)
- [ ] Implement `DocumentParser` for Markdown
- [ ] Implement `DocumentChunker` with heading preservation
- [ ] Configure chunk size (600 tokens) and overlap (80 tokens)
- [ ] Write unit tests for parsers and chunker

### Day 15-17: Vector Store + Embedding
- [ ] Initialize Qdrant client
- [ ] Create `documents` collection with vector config
- [ ] Implement `VectorStore.upsert()` for embeddings
- [ ] Implement `VectorStore.search()` for similarity search
- [ ] Implement `IngestionPipeline` (parse → chunk → embed → store)
- [ ] Write integration tests with Qdrant

### Day 18-19: Hybrid Search + Reranking
- [ ] Implement hybrid search (vector + keyword)
- [ ] Implement result reranking
- [ ] Implement filters (document_id, chunk_index)
- [ ] Optimize search for claim-specific queries
- [ ] Write search tests

### Day 20-21: Reliability Scoring
- [ ] Implement `EvidenceReliabilityScorer`
- [ ] Configure authority map by source type
- [ ] Implement weighted scoring (authority, recency, specificity, independence, retrieval)
- [ ] Implement relevance scoring
- [ ] Write scoring tests

### Day 22: API + Integration
- [ ] Create `POST /v1/documents` endpoint (upload)
- [ ] Create `GET /v1/runs/{run_id}/evidence` endpoint (search)
- [ ] Integrate with reasoning engine
- [ ] Run end-to-end test
- [ ] Write Dockerfile

## Definition of Done
- [ ] Documents ingested and chunked correctly
- [ ] Vector embeddings stored in Qdrant
- [ ] Search returns relevant results
- [ ] Reliability scoring produces reasonable scores
- [ ] API endpoints for upload and search work

## Risks
- **Large documents:** Implement chunking limits
- **Embedding quality:** Use proven models (nomic-embed-text, bge-m3)

## Retro Notes
- _To be filled after sprint completion_
