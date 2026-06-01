import boto3
from shared.config import get
from shared.logger import get_logger

logger = get_logger(__name__)

def get_dynamodb_table():
    table_name = get("DYNAMODB_REVIEWS_TABLE", "reviews")
    region     = get("AWS_REGION", "us-east-1")

    logger.info(f"ReviewDB - rozpoczynam połączenie z DynamoDB, tabela={table_name}...")
    try:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=region,
            aws_access_key_id=get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get("AWS_SECRET_ACCESS_KEY"),
        )
        table = dynamodb.Table(table_name)
        table.table_status
        logger.info(f"ReviewDB - połączenie z DynamoDB nawiązane pomyślnie, tabela={table_name}")
        return table
    except Exception as e:
        logger.error(f"ReviewDB - błąd połączenia z DynamoDB: {e}")
        raise
