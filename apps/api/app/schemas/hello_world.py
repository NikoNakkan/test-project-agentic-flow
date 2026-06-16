from pydantic import BaseModel, Field


class HelloWorldCount(BaseModel):
    count: int = Field(ge=0, description="Total number of Hello World button clicks")
