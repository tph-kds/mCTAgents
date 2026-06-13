# Security, Governance, and Sandboxing

## 1. Security philosophy

mCTAgents will connect models, tools, memory, documents, and external agents. This creates risk. Security must be designed into the tool gateway, evidence pipeline, runtime, and UI.

## 2. Main risks

```text
prompt injection through documents
tool misuse
malicious MCP servers
untrusted plugin code
secret leakage
cross-tenant data exposure
unsafe code execution
model provider key leakage
unbounded spending
unreviewed external agent delegation
```

## 3. Tool permission model

Every tool has a policy:

```yaml
tool: github_create_pr
risk_level: medium
requires_approval: true
allowed_agents:
  - coding_agent
  - maintainer_agent
rate_limit:
  per_run: 2
audit: true
```

## 4. Tool gateway rules

```text
- all tool calls go through the gateway
- no direct tool access from agent runtime
- validate tool input schema
- sanitize tool output
- attach tool result provenance
- log approval boundary
- enforce tenant/project permissions
```

## 5. Document safety

```text
- mark uploaded docs as untrusted
- isolate instructions from evidence
- detect prompt injection patterns
- never allow retrieved text to override system/developer policy
- show source provenance
```

## 6. Sandbox execution

For code/tool execution:

```text
MVP: disabled by default
Phase 2: Docker sandbox with read-only mounts and network controls
Phase 3: ephemeral workspace service
Phase 4: Kubernetes sandbox workers with quotas
```

## 7. Multi-tenancy

```text
tenant_id on every table
project_id on every run
row-level access checks
separate object storage prefixes
audit events for all sensitive actions
per-tenant API keys and quotas
```

## 8. Governance

```text
agent registry review
plugin signing later
benchmark before official plugin acceptance
security.md
responsible disclosure
threat model document
```
