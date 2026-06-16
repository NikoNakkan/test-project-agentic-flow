# Contract summary — TASK-001

> Written by **be-api-contract** (step 2).

## Endpoints

| Method | Path | operationId | Request | Response |
|--------|------|---------------|---------|----------|
| GET | `/hello-world/count` | `getHelloWorldCount` | — | `HelloWorldCount` |
| POST | `/hello-world/click` | `incrementHelloWorldCount` | — | `HelloWorldCount` |

## Schemas

### HelloWorldCount

```json
{ "count": 0 }
```

| Field | Type | Constraints |
|-------|------|-------------|
| `count` | integer | `minimum: 0` |

## Files

| File | Purpose |
|------|---------|
| `packages/contract/openapi.yaml` | OpenAPI 3.1 source of truth |
| `packages/contract/types.ts` | Shared TS type for FE |
| `packages/contract/package.json` | Package exports |

## Notes for be-dev

- Both endpoints return the same `HelloWorldCount` schema.
- `POST /hello-world/click` has no request body — increment is implicit.
- Counter is in-memory (not in contract — implementation detail).
