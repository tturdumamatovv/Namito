FROM python:3.10

ENV APP_HOME /app

WORKDIR $APP_HOME

# Copy all requirements files from the requirements directory
COPY /namito/requirements/*.txt ./requirements/

# Install dependencies from all requirements files
RUN pip install --no-cache-dir -r ./requirements/base.txt \
    && pip install --no-cache-dir -r ./requirements/local.txt \
    && pip install --no-cache-dir -r ./requirements/production.txt

# Copy the rest of the application code
COPY . .

# Specify any additional commands needed for your application setup
# For example, database migrations, static files collection, etc.

# Command to run your application
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8013" ]
