# Schema Validation Skill

## Purpose

Validate that all protocol objects conform to JSON schemas.

## When to Use

- Adding new protocol objects
- Modifying existing schemas
- Testing API endpoints
- Debugging validation errors

## Schema Location

All schemas live in `packages/core-protocol/schemas/`

## Core Schemas

- `problem-frame.json`
- `claim.json`
- `evidence.json`
- `objection.json`
- `revision.json`
- `decision.json`
- `final-answer.json`
- `event.json`

## Validation Rules

1. All objects must have required fields
2. IDs must follow naming convention: `{type}_{uuid}`
3. Timestamps must be ISO 8601 format
4. Confidence scores must be between 0.0 and 1.0
5. Status fields must use allowed enum values

## Example Validation

```python
from pydantic import BaseModel
from packages.core_protocol import Claim

def validate_claim(data: dict) -> Claim:
    """Validate and parse a claim object."""
    return Claim.model_validate(data)
```

## Testing

```bash
# Run schema validation tests
pytest tests/unit/test_schema.py -v

# Validate specific object
pytest tests/unit/test_schema.py::test_claim_validation -v
```
