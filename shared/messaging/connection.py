import pika, os, ssl, certifi
from dotenv import load_dotenv

load_dotenv()

def get_connection() -> pika.BlockingConnection:
    url = os.getenv("AMQP_URL")
    params = pika.URLParameters(url)
    params.ssl_options = pika.SSLOptions(
        context=ssl.create_default_context(cafile=certifi.where())
    )
    return pika.BlockingConnection(params)
