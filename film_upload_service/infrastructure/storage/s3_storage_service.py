import boto3, os
from shared.logger import get_logger

logger = get_logger(__name__)

class S3StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.bucket = os.getenv("AWS_S3_BUCKET", "cinema-uploads")
        logger.info("S3StorageService.__init__()")

    def upload_file(self, file_content: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        logger.info(f"S3StorageService.upload_file() - key={key}, size={len(file_content)}")
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_content,
            ContentType=content_type,
        )
        logger.info(f"S3StorageService.upload_file() - uploaded to s3://{self.bucket}/{key}")
        return key

    def get_presigned_url(self, key: str, expiration: int = 3600) -> str:
        logger.info(f"S3StorageService.get_presigned_url() - key={key}")
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiration,
        )
        return url
