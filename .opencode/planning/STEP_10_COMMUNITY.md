# STEP 10: Community & Ecosystem

**Timeline:** Days 35-45 | **Complexity:** 2/5 | **Dependencies:** STEPs 0-9

## Goal

Community infrastructure for open-source adoption.

## Files to Create

```
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── examples/
│   ├── notebooklm-style/
│   ├── software-architecture-review/
│   ├── research-debate/
│   ├── security-review/
│   └── product-decision/
├── integrations/
│   ├── langchain/
│   ├── llamaindex/
│   └── openai/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       ├── benchmark.yml
│       └── release.yml
```

## Contributing Workflow
1. Fork repository
2. Clone and `make setup-dev`
3. `make docker-up` to start services
4. Create branch: `git checkout -b feat/my-feature`
5. Make changes, run `make lint` and `make test`
6. Commit with conventional commits
7. Push and create PR

## Example Verticals
Each example includes:
- README with setup instructions
- Problem statement
- Expected agent society
- Sample output

## Integration Guides
- **LangChain:** Use mCTAgents as a tool
- **LlamaIndex:** Connect to pipelines
- **OpenAI:** Use alongside function calling

## CI Pipeline
- Schema validation
- Python tests (pytest)
- Go tests (go test)
- Frontend build (Next.js)
- Docker Compose smoke test

## Success Criteria
- [ ] CONTRIBUTING.md complete
- [ ] 3+ example verticals working
- [ ] CI pipeline passes
- [ ] Issue and PR templates created
- [ ] Integration guides written
