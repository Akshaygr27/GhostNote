from datetime import datetime

from beanie import Document, Indexed


class RevokedToken(Document):

    jti: Indexed(str, unique=True)

    expires_at: Indexed(
        datetime,
        expireAfterSeconds=0
    )

    class Settings:
        name = "revoked_tokens"