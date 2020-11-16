from fastapi import FastAPI, Header, Body, Path
from app.app.api import api_router
from app.app import inital_data

app = FastAPI()


@app.get("/header")
def header(token: int = Body(..., gt=0, embed=True)):
    return {"token values": token}


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(api_router)
