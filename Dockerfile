FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./namito/requirements/production.txt .

RUN pip install -r production.txt

COPY . .
