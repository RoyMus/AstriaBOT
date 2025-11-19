FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared requirements
COPY shared/requirements.txt shared-requirements.txt
RUN pip install -r shared-requirements.txt

# Copy service requirements
COPY services/message-service/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application code
COPY services/message-service /app/services/message-service
COPY shared /app/shared
COPY Utils /app/Utils
COPY db /app/db
COPY .env .env

# Install Azure Functions Core Tools
RUN pip install azure-functions

ENV AzureWebJobsScriptRoot=/app/services/message-service

CMD ["func", "start", "--port", "80"]
