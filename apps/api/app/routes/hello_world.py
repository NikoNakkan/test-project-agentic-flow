from fastapi import APIRouter

from app.schemas.hello_world import HelloWorldCount
from app.services import hello_world as hello_world_service

router = APIRouter(prefix="/hello-world", tags=["hello-world"])


@router.get("/count", response_model=HelloWorldCount)
def get_hello_world_count() -> HelloWorldCount:
    return HelloWorldCount(count=hello_world_service.get_count())


@router.post("/click", response_model=HelloWorldCount)
def increment_hello_world_count() -> HelloWorldCount:
    count = hello_world_service.increment()
    return HelloWorldCount(count=count)
