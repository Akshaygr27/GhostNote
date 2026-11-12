import uuid

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt

from bson import ObjectId

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User
from app.models.revoked_token import RevokedToken


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Generate JWT with unique token ID

def create_access_token(subject: str):

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# Verify JWT and check revocation

async def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict[str, Any]:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        token_id = payload.get("jti")

        if (
            not isinstance(user_id, str)
            or not ObjectId.is_valid(user_id)
            or not isinstance(token_id, str)
        ):
            raise credentials_exception

    except InvalidTokenError as exc:

        raise credentials_exception from exc

    # Check whether token has been revoked

    revoked_token = await RevokedToken.find_one(
        RevokedToken.jti == token_id
    )

    if revoked_token is not None:
        raise credentials_exception

    return payload


# Get authenticated user

async def get_current_user(
    payload: Annotated[
        dict[str, Any],
        Depends(get_token_payload)
    ]
):

    user_id = payload["sub"]

    user = await User.get(ObjectId(user_id))

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user