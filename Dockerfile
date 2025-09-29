FROM python:3.14.0rc3-slim-trixie

RUN apt update && apt install -y pkg-config gcc \
    default-libmysqlclient-dev pkg-config
RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD [ "python", "./chatbot/manage.py", "runserver", "0.0.0.0:8000" ]
