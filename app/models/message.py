from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class Message(Document):

    content: str

    is_anonymous: bool = True

    likes_count: int = Field(default=0, ge=0)

    liked_by: list[str] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "messages"