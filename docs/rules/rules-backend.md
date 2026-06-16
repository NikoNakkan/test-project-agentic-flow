
# Backend rules (FastAPI)

## Architecture & Code Organization
- 4-layer architecture:
  - Endpoints → minimal logic
  - Services → no db.execute
  - Repositories → DB access only
  - Entities → ORM models

## Layer rules
- Endpoints:
  - use APIRouter
  - inject AsyncSession + current_user

- Service:
  - business logic ONLY
  - never call db directly

- Repository:
  - async DB access
  - return Entities (NOT Pydantic)

- Entities:
  - inherit Base + TimestampedModel

## DB & ORM
- AsyncSession ONLY
- Depends(get_db)
- Mapped[type]
- mapped_column()

## Logging
- use loguru
logger.bind(operation="Audit").info(...)

## Error handling (SHORT version here)
- use custom HTTPExceptions
- never stdlib exceptions
