from fastapi import APIRouter

router = APIRouter()


# Add methods for interacting with desktop

@router.get("/echo/{tmp}")
async def echo(tmp: int):
    return {'echo': tmp}
