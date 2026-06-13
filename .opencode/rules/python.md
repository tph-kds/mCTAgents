# Python Coding Rules

## Style
- **Formatter:** Ruff (replaces Black, isort, Flake8)
- **Type Checker:** mypy
- **Min Version:** Python 3.11+

## Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

## Imports
- Order: stdlib, third-party, local
- Use absolute imports within packages
- Group imports with blank lines between groups

## Type Hints
- All function signatures must have type hints
- Use `Optional[T]` or `T | None` for nullable types
- Use `Union[T1, T2]` or `T1 | T2` for unions
- Use `list[T]`, `dict[K, V]` (lowercase) for generics

## Data Models
- Use Pydantic v2 models for all data structures
- Never use raw dicts for structured data
- Define JSON schemas for all protocol objects

## Error Handling
- Use custom exception classes per service
- Never swallow exceptions silently
- Log exceptions with structured context
- Use `try/except` with specific exception types

## Async
- Use `async/await` for I/O-bound operations
- Prefer `httpx` over `requests` for HTTP clients
- Use `asyncpg` for PostgreSQL, `aioredis` for Redis

## Testing
- Use pytest with fixtures
- Test file naming: `test_<module>.py`
- Test function naming: `test_<description>`
- Use `conftest.py` for shared fixtures
- Mock external services in unit tests

## Documentation
- Use docstrings for public functions
- Keep docstrings concise (one-line for simple functions)
- Document complex algorithms and business logic
