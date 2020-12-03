FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN export GOOGLE_APPLICATION_CREDENTIALS="/app/app/app/server-7f82a-firebase-adminsdk-leob0-c2693700d5.json"

WORKDIR ./app/app