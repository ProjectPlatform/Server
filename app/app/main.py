import logging
import uvicorn
from fastapi import FastAPI
from starlette.routing import WebSocketRoute

from app.app import inital_data
from app.app.api.api import api_router
from app.app.src.websockets import ConnectionManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

routes = [WebSocketRoute("/ws", ConnectionManager)]
app = FastAPI(
    docs_url="/",
    title="Backend server",
    description="What's new:\n 1. Now, when you register, you will receive an email with verification code (check "
                "your email and don't forget send it using method 'verification')\n "
                "2. The field 'message_type' has been added to the message (to determine the type of "
                "message)\n "
                "3. Now you can download files from server. Check the method 'get_attachments'\n"
                "4. When a user is added or removed to the chat, a notification is sent (you can identify "
                "it by the sender's id. It is equal to 1)\n"
                "5. Added system message when chat was creating\n"
                "6. In case deleting user, the id field in all his messages takes the value = 2 (which matched to the "
                "user DELETED) ",
    version="0.0.21",
    routes=routes
)

app.include_router(api_router)

# For DEBUG
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
