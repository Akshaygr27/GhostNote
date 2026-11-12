from typing import (Annotated, Any)
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.models.revoked_token import RevokedToken
from app.core.security import (get_token_payload, get_current_user, create_access_token)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User

from app.schemas.auth import (
    UserCreate,
    UserPublic,
    Token
)

from app.services.auth_service import (
    register_user,
    authenticate_user
)

from app.core.security import (
    create_access_token,
    get_current_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Convert database user to public response

def user_response(user: User):

    return UserPublic(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


# USER REGISTRATION

@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
async def register(data: UserCreate):

    user = await register_user(data)

    return user_response(user)


# USER LOGIN

@router.post(
    "/login",
    response_model=Token
)
async def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ]
):

    user = await authenticate_user(
        form_data.username,
        form_data.password
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


# PROTECTED USER PROFILE

@router.get(
    "/me",
    response_model=UserPublic
)
async def get_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user)
    ]
):

    return user_response(current_user)

@router.post("/logout")
async def logout(
    payload: Annotated[
        dict[str, Any],
        Depends(get_token_payload)
    ]
):

    token_id = payload["jti"]

    expires_at = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc
    )

    collection = RevokedToken.get_pymongo_collection()

    await collection.update_one(
        {"jti": token_id},
        {
            "$setOnInsert": {
                "jti": token_id,
                "expires_at": expires_at
            }
        },
        upsert=True
    )

    return {
        "success": True,
        "message": "Successfully logged out"
    }