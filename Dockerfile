FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

WORKDIR ./app/app