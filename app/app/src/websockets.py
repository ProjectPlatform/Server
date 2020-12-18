from typing import Dict
import logging

from fastapi import WebSocket
from starlette.endpoints import WebSocketEndpoint

from app.app.src.security import decode_token

log = logging.getLogger(__name__)


class Connections:
    def __init__(self, ):
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
        user_id = await decode_token(websocket.headers["Authorization"])
        user_id = user_id["id"]
        log.info(user_id)
        connections.add_user(user_id, websocket)
        await websocket.accept()

    async def on_disconnect(self, _websocket: WebSocket, _close_code: int):
        user_id = await decode_token(_websocket.headers["Authorization"])
        user_id = user_id["id"]

        connections.remove_user(user_id)

    async def on_receive(self, _websocket: WebSocket, msg: str):
        log.info("receive")
