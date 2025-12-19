FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app
WORKDIR ${APP_HOME}

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# This will fail if the local `config_example.py` hasn't been updated
# to include working API keys. WARNING: do not follow this pattern for
# a production system (baking sensitive data into the config and into
# the running image), this is just a prototype
COPY config.py .env

# Copy the application code and scripts. These are mounted when
# running the app locally with compose
COPY ./src/ src/
COPY ./scripts/ scripts/

EXPOSE 8000
COPY run.sh run.sh
RUN chmod +x run.sh
CMD ["/app/run.sh"]
