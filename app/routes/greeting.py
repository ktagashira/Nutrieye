from fastapi import APIRouter


greeting_router = APIRouter(prefix="/greeting", tags=["greeting"])


@greeting_router.get("/")
async def greeting():
    return {"message": "Hello, World!"}
