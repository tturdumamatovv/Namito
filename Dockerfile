FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./namito/requirements/base.txt .

RUN pip install -r base.txt

COPY . .
