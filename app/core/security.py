from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt

from bson import ObjectId

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User


# Password hashing configuration

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# OAuth2 configuration

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Hash password

def hash_password(password: str):

    return pwd_context.hash(password)


# Verify password

def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# Generate JWT token

def create_access_token(subject: str):

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token


# Verify JWT and retrieve user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):

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

        if not isinstance(user_id, str):
            raise credentials_exception

        if not ObjectId.is_valid(user_id):
            raise credentials_exception

    except InvalidTokenError:

        raise credentials_exception

    user = await User.get(ObjectId(user_id))

    if user is None:
        raise credentials_exception

    return user