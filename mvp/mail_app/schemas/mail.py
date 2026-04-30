from datetime import datetime

from pydantic import BaseModel, Field

try:
    # Pydantic v2
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover (Pydantic v1)
    ConfigDict = None


# information about the mail
class MailSchema(BaseModel):
    id: int = Field(..., description="id of the mail")
    title: str = Field(default="", description="title of the mail")
    description: str = Field(default="", description="description of the mail")
    created_at: datetime = Field(..., description="created time")
    category: str | None = Field(default=None, description="category of the mail")

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class ResponseSchema(BaseModel):
    message: str = Field(default="", description="result of the operation")

