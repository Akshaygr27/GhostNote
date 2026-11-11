from bson import ObjectId

from fastapi import HTTPException

from app.models.message import Message

from pymongo.errors import PyMongoError


# Create message

async def create_message(content: str):

    message = Message(
        content=content,
        is_anonymous=True
    )

    await message.insert()

    return message


# Get messages with pagination

async def get_messages(
    limit: int = 20,
    offset: int = 0
):

    messages = await (
        Message.find_all()
        .sort("-created_at")
        .skip(offset)
        .limit(limit)
        .to_list()
    )

    return messages


# Like a message

async def like_message(
    message_id: str,
    user_id: str
):

    # Validate MongoDB ObjectId

    if not ObjectId.is_valid(message_id):

        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    object_id = ObjectId(message_id)

    # Get MongoDB collection

    collection = Message.get_pymongo_collection()

    try:

        # Atomic update:
        # Add user ID only if it does not already exist.
        # Increment likes_count only when the user is new.

        result = await collection.update_one(

            {
                "_id": object_id,
                "liked_by": {"$ne": user_id}
            },

            {
                "$addToSet": {
                    "liked_by": user_id
                },

                "$inc": {
                    "likes_count": 1
                }
            }
        )

    except PyMongoError:

        raise HTTPException(
            status_code=500,
            detail="Unable to process like"
        )

    # Fetch updated message

    message = await Message.get(object_id)

    if message is None:

        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    # If matched_count is zero, user already liked it

    already_liked = result.matched_count == 0

    return message, already_liked