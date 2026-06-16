# API routes (backend)

Grouped by domain for easier scanning.
Top node = handler file path. One row per route.

---

## apps/api/app/routes/hello_world.py

| symbol_id | method | path | handler | request_type | response_type | tests |
|-----------|--------|------|---------|--------------|---------------|-------|
| 1 | GET | `/hello-world/count` | get_hello_world_count | — | HelloWorldCount | apps/api/tests/test_hello_world.py |
| 2 | POST | `/hello-world/click` | increment_hello_world_count | — | HelloWorldCount | apps/api/tests/test_hello_world.py |
