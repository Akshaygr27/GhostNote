from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():

    return {
        "status": "success",
        "message": "FastAPI is running"
    }