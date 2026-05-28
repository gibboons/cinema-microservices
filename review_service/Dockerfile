FROM python:3.11-slim
WORKDIR /app
COPY review_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY review_service/ .
