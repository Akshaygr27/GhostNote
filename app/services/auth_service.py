from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from app.models.user import User
from app.schemas.auth import UserCreate

from app.core.security import (
    hash_password,
    verify_password
)


# Dummy hash for unknown usernames

DUMMY_HASH = hash_password("dummy-password-for-checking")


# Register user

async def register_user(data: UserCreate):

    # Check existing username or email

    existing_user = await User.find_one({
        "$or": [
            {"username": data.username},
            {"email": str(data.email)}
        ]
    })

    if existing_user:

        if existing_user.username == data.username:

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Hash password without blocking async event loop

    hashed_password = await run_in_threadpool(
        hash_password,
        data.password
    )

    # Create user document

    user = User(
        username=data.username,
        email=str(data.email),
        hashed_password=hashed_password
    )

    try:

        await user.insert()

    except DuplicateKeyError:

        # Handles simultaneous registration attempts

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return user


# Authenticate user

async def authenticate_user(
    username_or_email: str,
    password: str
):

    identifier = username_or_email.strip().lower()

    user = await User.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })

    if user is None:

        await run_in_threadpool(
            verify_password,
            password,
            DUMMY_HASH
        )

        return None

    password_valid = await run_in_threadpool(
        verify_password,
        password,
        user.hashed_password
    )

    if not password_valid:
        return None

    return user