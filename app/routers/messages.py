from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from app.models.user import User

from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    LikeResponse
)

from app.services.message_service import (
    create_message,
    get_messages,
    like_message
)

from app.core.security import get_current_user


router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


# Convert MongoDB document to public response

def message_response(message):

    return MessageResponse(
        id=str(message.id),
        content=message.content,
        is_anonymous=message.is_anonymous,
        likes_count=message.likes_count,
        created_at=message.created_at
    )


# 1. CREATE MESSAGE

@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def submit_message(

    data: MessageCreate,

    current_user: Annotated[
        User,
        Depends(get_current_user)
    ]

):

    message = await create_message(data.content)

    return message_response(message)


# 2. GET ALL MESSAGES

@router.get(
    "",
    response_model=list[MessageResponse],
)
async def list_messages(

    current_user: Annotated[
        User,
        Depends(get_current_user)
    ],
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    offset: int = Query(
        default=0,
        ge=0
    )

):

    messages = await get_messages(
        limit=limit,
        offset=offset
    )

    return [
        MessageResponse(
            id=str(message.id),
            content=message.content,
            is_anonymous=message.is_anonymous,
            likes_count=message.likes_count,
            created_at=message.created_at,
            liked_by_current_user=(
                str(current_user.id) in message.liked_by
            )
        )
        for message in messages
    ]


# 3. LIKE MESSAGE

@router.post(
    "/{message_id}/like",
    response_model=LikeResponse
)
async def like_message_endpoint(

    message_id: str,

    current_user: Annotated[
        User,
        Depends(get_current_user)
    ]

):

    message, already_liked = await like_message(
        message_id=message_id,
        user_id=str(current_user.id)
    )

    return LikeResponse(
        message_id=str(message.id),
        likes_count=message.likes_count,
        liked=True,
        already_liked=already_liked
    )