FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY namito/requirements/base.txt .
COPY namito/requirements/local.txt .
COPY namito/requirements/production.txt .

RUN pip install -r base.txt
RUN pip install -r local.txt
RUN pip install -r local.txt

COPY . .
