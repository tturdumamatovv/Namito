FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./namito/requirements .

RUN pip install -r requirements/base.txt
RUN pip install -r requirements/local.txt
RUN pip install -r requirements/production.txt

COPY . .
