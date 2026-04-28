from pydantic import BaseModel, Field

# define the schema for the mail data

# information about the mail
class MailSchema(BaseModel):
    title: str = Field(default="", description="title of the mail")
    description: str = Field(default="", description="description of the mail")
    id: int=Field(..., description="id of the mail")
    category: str | None = Field(default=None, description="category of the mail")

class ResponseSchema(BaseModel):
    message: str = Field(default="", description="result of the operation")

