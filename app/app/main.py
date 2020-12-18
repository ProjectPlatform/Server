import logging

import uvicorn
from app.app import inital_data
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.routing import WebSocketRoute, Route
from app.app.api import api_router
from app.app.src.websockets import ConnectionManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

routes = [WebSocketRoute("/ws", ConnectionManager)]
app = FastAPI(docs_url="/",
              title="Backend server",
              description="What's new:\n 1. Now, when you register, you receive an email with verification code (check "
                          "your email and don't forget send it using method 'verification')\n "
                          "2. The field 'message_type' has been added to the message (to determine the type of message)\n"
                          "3. Now you can download files from server. Check the method 'get_attachments'\n"
                          "4. When a user is added or removed to the chat, a notification is sent (you can identify it by the sender's id. It is equal to 1)",
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
            var ws = new WebSocket("ws://localhost:8000/ws");
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
