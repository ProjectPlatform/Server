import logging
from app.app import inital_data
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.routing import WebSocketRoute
from app.app.api import api_router
from app.app.src.websockets import ConnectionManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

routes = [WebSocketRoute("/ws", ConnectionManager)]
app = FastAPI(
    docs_url="/",
    title="Backend server",
    description="What's new:\n 1. Now, when you register, you receive an email with verification code (check "
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

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            var ws = new WebSocket("ws://188.120.238.3:80/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/w")
async def get():
    return HTMLResponse(html)


app.include_router(api_router)

# For DEBUG
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
