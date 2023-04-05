FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.2.2

WORKDIR /code

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip3 install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /code/
RUN poetry install

COPY . /code/