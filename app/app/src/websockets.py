import random
from typing import Dict
import logging

import asyncio
from fastapi import WebSocket
from starlette.endpoints import WebSocketEndpoint

from app.app.backend import get_user_info
from app.app.src import security

log = logging.getLogger(__name__)


class Connections:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    def add_user(self, user_id: int, websocket: WebSocket):
        self.active_connections.update({user_id: websocket})

    def remove_user(self, user_id: int):
        self.active_connections.pop(user_id)


connections = Connections()


class ConnectionManager(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_connect(self, websocket, ):
        log.info("Connecting new user...")
        log.info(websocket.headers)
        # if websocket.headers.__contains__("Authorization"):
        #     user_id = await security.decode_token(websocket.headers["Authorization"])
        #     user_id = user_id["id"]
        # else:
        #     user_id = random.randint(1, 100)

        user_id = await security.decode_token(websocket.headers["Authorization"])
        user_id = user_id["id"]
        await websocket.accept()

        connections.add_user(user_id, websocket)
        log.info(connections.active_connections)

    async def on_disconnect(self, _websocket: WebSocket, _close_code: int):
        user_id = await security.decode_token(_websocket.headers["Authorization"])
        user_id = user_id["id"]

        connections.remove_user(user_id)
        log.info(f'{user_id} has been disconnected')
        await _websocket.close()

    async def on_receive(self, _websocket: WebSocket, msg: str):
        pass
        # log.info("receive")
        # log.info(msg)
        # if msg is not None:
        #     await _websocket.send_json(msg)
        #     user_id = await get_user_info(current_user=1, user_nick="pl")
        #     await _websocket.send_json(user_id)


async def bug():
    while True:
        log.info(connections.active_connections)
        await asyncio.sleep(3)
