from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=100,
        gt=0,
        le=100,
        description="Maximum number of records to return",
    )
