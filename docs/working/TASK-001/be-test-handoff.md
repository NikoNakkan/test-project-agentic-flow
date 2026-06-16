# Backend test handoff — TASK-001

> **Required** output from **be-dev** before the BE testing step.

## Files changed

- `apps/api/pyproject.toml`
- `apps/api/app/main.py`
- `apps/api/app/routes/hello_world.py`
- `apps/api/app/services/hello_world.py`
- `apps/api/app/schemas/hello_world.py`

## New or changed exports

| Symbol | File | Kind |
|--------|------|------|
| `get_hello_world_count` | `app/routes/hello_world.py` | route |
| `increment_hello_world_count` | `app/routes/hello_world.py` | route |
| `get_count` | `app/services/hello_world.py` | service |
| `increment` | `app/services/hello_world.py` | service |
| `reset_count` | `app/services/hello_world.py` | service |
| `HelloWorldCount` | `app/schemas/hello_world.py` | pydantic_model |
| `app` | `app/main.py` | FastAPI app |

## Testable behaviors

- `GET /hello-world/count` returns `200` with `{ "count": 0 }` on fresh server
- `POST /hello-world/click` returns `200` with `{ "count": 1 }` on first click
- Sequential clicks increment count: 1 → 2 → 3
- `GET /hello-world/count` reflects total after clicks
- Response `count` is always a non-negative integer

## Suggested test files

| Export | Test file |
|--------|-----------|
| `hello_world` service | `apps/api/tests/test_hello_world_service.py` |
| `hello_world` routes | `apps/api/tests/test_hello_world_routes.py` |

## Notes for be-testing-agent

- Use `hello_world_service.reset_count()` in pytest fixture/autouse to isolate tests
- Use FastAPI `TestClient` with `app` from `app.main`
- No database — pure in-memory state
