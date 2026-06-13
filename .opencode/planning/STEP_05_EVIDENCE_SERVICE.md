# STEP 5: Evidence Service

**Timeline:** Days 12-22 | **Complexity:** 4/5 | **Dependencies:** STEPs 0, 1

## Goal

Document ingestion, chunking, embedding, vector search, and evidence scoring.

## Pipeline

```
Document → Parse → Chunk → Embed → Store (Qdrant)
                                      ↓
Query → Embed → Vector Search → Rerank → Evidence Results
```

## Supported Formats
- PDF (PyMuPDF)
- DOCX (python-docx)
- Markdown
- Plain text

## Chunking Strategy
- Chunk size: 600 tokens
- Overlap: 80 tokens
- Preserve headings
- Track page/section metadata

## Evidence Reliability Scoring

| Factor | Weight | Source |
|--------|--------|--------|
| Source Authority | 0.25 | Document type ranking |
| Specificity | 0.25 | How specific to the claim |
| Retrieval Confidence | 0.20 | Vector similarity score |
| Recency | 0.15 | Document age |
| Independence | 0.15 | Source diversity |

## Files
```
services/evidence-service/
├── src/mctagents/
│   ├── ingestion/     # Parser, chunker, pipeline
│   ├── retrieval/     # Vector store, hybrid search
│   ├── scoring/       # Reliability, relevance
│   └── api/           # REST endpoints
└── tests/
```

## Success Criteria
- [ ] Documents ingested and chunked correctly
- [ ] Vector embeddings stored in Qdrant
- [ ] Search returns relevant results
- [ ] Reliability scoring produces reasonable scores
- [ ] API endpoints work
