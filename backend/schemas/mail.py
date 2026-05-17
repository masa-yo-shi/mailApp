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
    user_id: int = Field(..., description="id of the user who created the mail")

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True

class MailResponseSchema(BaseModel):
    id : int = Field(..., description="id of the mail response")
    response_title: str = Field(default="", description="title of the mail response")
    response_description: str = Field(default="", description="description of the mail response")

class ResponseSchema(BaseModel):
    message: str = Field(default="", description="result of the operation")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserPublic(BaseModel):
    id: int = Field(..., description="id of the user")
    username: str = Field(..., description="username of the user")

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class UserInDB(BaseModel):
    id: int = Field(..., description="id of the user")
    username: str = Field(..., description="username of the user")
    hashed_password: str

    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True

