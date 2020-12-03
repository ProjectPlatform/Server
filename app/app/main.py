import uvicorn
from fastapi import FastAPI
from app.app.api import api_router
from app.app import inital_data

app = FastAPI(docs_url="/",
              title="Backend server",
              description="Server for platform application",
              version="0.0.2",
              )

app.include_router(api_router)


# For DEBUG
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
