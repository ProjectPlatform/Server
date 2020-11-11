from fastapi import FastAPI
from app.app.api.login import router
from app.app import inital_data

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/echo")
def read_root(echo: str):
    return {"echo": echo}


# app = FastAPI(root_path="/api/v1")
app.include_router(router)
