FROM python:3.11-slim

RUN apt update && apt install -y pkg-config gcc \
    default-libmysqlclient-dev pkg-config \
    libhdf5-dev build-essential
RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_md-3.7.0/es_core_news_md-3.7.0-py3-none-any.whl

COPY . .
RUN chmod 755 ./entrypoint.sh
EXPOSE 8000

ENTRYPOINT [ "./entrypoint.sh" ]

