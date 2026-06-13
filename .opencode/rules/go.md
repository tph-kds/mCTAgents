# Go Coding Rules

## Style
- **Formatter:** gofmt
- **Linter:** golangci-lint

## Naming Conventions
- `camelCase` for unexported identifiers
- `PascalCase` for exported identifiers
- Use short variable names in small scopes

## Error Handling
- Handle errors explicitly; never use `_` to discard
- Use `fmt.Errorf` with `%w` for error wrapping
- Return errors, don't panic
- Use sentinel errors for expected conditions

## Context
- Pass `context.Context` as first parameter
- Use context for cancellation and timeouts
- Don't store context in structs

## Testing
- Use table-driven tests
- Name test files `*_test.go`
- Use `testing.T` for unit tests
- Use `testify` for assertions (optional)

## Project Layout
- Follow Go project layout conventions
- Keep packages focused and small
- Use internal/ for private packages
- Define interfaces where consumed
