# TypeScript / Next.js Coding Rules

## Style
- **Formatter:** Prettier
- **Linter:** ESLint
- **Type Checker:** TypeScript strict mode

## Naming Conventions
- `PascalCase` for components, types, interfaces
- `camelCase` for functions, variables, props
- `UPPER_SNAKE_CASE` for constants
- `kebab-case` for file names

## Components
- Use functional components with hooks
- Prefer named exports over default exports
- Keep components small and focused
- Extract logic into custom hooks

## Types
- Use `interface` for object shapes
- Use `type` for unions and intersections
- Avoid `any` type; use `unknown` and narrow
- Use Zod for runtime validation

## State Management
- Use React hooks for local state
- Use React Query for server state
- Avoid global state unless necessary

## API Integration
- Use the SSE client for event streaming
- Handle loading and error states
- Use proper TypeScript types for API responses

## Testing
- Use Vitest or Jest for unit tests
- Use React Testing Library for component tests
- Test user interactions, not implementation details
