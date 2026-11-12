import unicodedata
import nh3

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# Request schema

class MessageCreate(BaseModel):

    content: str = Field(
        min_length=1,
        max_length=2000
    )

    @field_validator("content", mode="before")
    @classmethod
    def sanitize_content(cls, value):

        if not isinstance(value, str):
            return value

        # Remove unwanted control characters
        value = "".join(
            char for char in value
            if char in "\n\t"
            or unicodedata.category(char) != "Cc"
        )

        # Remove HTML tags and unsafe markup
        value = nh3.clean(
            value,
            tags=set(),
            attributes={}
        )

        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        return value


# Response schema

class MessageResponse(BaseModel):

    id: str
    content: str
    is_anonymous: bool
    likes_count: int
    created_at: datetime
    liked_by_current_user: bool = False


# Like response schema

class LikeResponse(BaseModel):

    message_id: str
    likes_count: int
    liked: bool
    already_liked: bool