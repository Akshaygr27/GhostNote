from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)


class UserCreate(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$"
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72
    )

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value):

        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):

        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value):

        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")

        return value


class UserPublic(BaseModel):

    id: str
    username: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):

    access_token: str
    token_type: str = "bearer"