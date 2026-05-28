FROM python:3.11-slim
WORKDIR /app
COPY rating_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY rating_service/ .
