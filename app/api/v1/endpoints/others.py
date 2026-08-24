
from fastapi import APIRouter, Header


router = APIRouter(prefix="/others", tags=["others"])


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/greet")
async def greet(name: str = "Guest", age: int = 30):
    return {"message": f"Hello, {name}!, You are {age} years old."}


@router.get("/get-headers")
async def get_headers(
    accept: str = Header(None),
    user_agent: str = Header(None),
    content_type: str = Header(None),
    host: str = Header(None)
):
    requested_headers = {
        "Accept": accept,
        "User-Agent": user_agent,
        "Content-Type": content_type,
        "Host": host
    }
    return {"requested_headers": requested_headers}
