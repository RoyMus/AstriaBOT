FROM python:3.11-slim

WORKDIR /app

COPY shared/requirements.txt shared-requirements.txt
RUN pip install -r shared-requirements.txt

COPY services/payment-service/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY services/payment-service /app/services/payment-service
COPY shared /app/shared
COPY Utils /app/Utils
COPY db /app/db
COPY .env .env

RUN pip install azure-functions

ENV AzureWebJobsScriptRoot=/app/services/payment-service

CMD ["func", "start", "--port", "80"]
