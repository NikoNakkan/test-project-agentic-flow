# Backend services

Domain and service functions. Top node = source file path.

## apps/api/app/services/hello_world.py

| symbol_id | name | purpose | tests | depends_on |
|-----------|------|---------|-------|------------|
| 3 | get_count | Return current in-memory Hello World click count | apps/api/tests/test_hello_world.py |  |
| 4 | increment | Increment click counter by one and return new total | apps/api/tests/test_hello_world.py |  |
| 5 | reset_count | Reset counter to zero (test isolation only) | apps/api/tests/test_hello_world.py |  |
