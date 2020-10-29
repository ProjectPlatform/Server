from fastapi import FastAPI
from api.login import *

app = FastAPI(root_path="/api/v1")

#file_path = "/home/kondrahin/Lections/2020-10-03-13-41-32.mkv"


# @app.get("/echo/{tmp}")
# async def echo(tmp: int):
#     return {'echo': tmp}
#
#
# @app.get("/file/{name}")
# def send_file():
#     return FileResponse(file_path)
#
#
# @app.get("/echo")
# def echo_body(tmp: str):
#     return {'echo': tmp}


app.include_router(router)
