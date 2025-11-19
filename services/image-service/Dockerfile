FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY shared/requirements.txt shared-requirements.txt
RUN pip install -r shared-requirements.txt

COPY services/image-service/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY services/image-service /app/services/image-service
COPY shared /app/shared
COPY Utils /app/Utils
COPY db /app/db
COPY .env .env

RUN pip install azure-functions

ENV AzureWebJobsScriptRoot=/app/services/image-service

CMD ["func", "start", "--port", "80"]
