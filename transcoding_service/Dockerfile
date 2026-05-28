FROM python:3.11-slim
WORKDIR /app
COPY transcoding_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY transcoding_service/ .
