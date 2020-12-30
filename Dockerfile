FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app/app

COPY ./requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN export GOOGLE_APPLICATION_CREDENTIALS="/app/app/app/server-7f82a-firebase-adminsdk-leob0-215c5fb60a.json"

WORKDIR ./app/app

CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "80"]
