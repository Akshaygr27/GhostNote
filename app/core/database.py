from pymongo import AsyncMongoClient
from beanie import init_beanie

from app.core.config import settings
from app.core.logging_config import logger

from app.models.user import User
from app.models.message import Message

from app.models.revoked_token import RevokedToken

client = None


async def connect_to_mongodb():

    global client

    try:

        client = AsyncMongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )

        # Check database connection
        await client.admin.command("ping")

        # Initialize Beanie
        await init_beanie(
            database=client[settings.DATABASE_NAME],
            document_models=[
                User,
                Message,
                RevokedToken
            ]
        )

        logger.info("MongoDB connected successfully")

    except Exception:

        logger.exception("MongoDB connection failed")

        if client is not None:
            await client.close()
            client = None

        raise


async def close_mongodb():

    global client

    if client is not None:

        await client.close()

        client = None

        logger.info("MongoDB connection closed")