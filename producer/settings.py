import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

RABBITMQ_URL=os.getenv(
    "RABBITMQ_URL",
    default="amqp://guest:guest@localhost/",
)
print("settings,rabbitmq_url: ", RABBITMQ_URL)

QUEUE_NAME=os.getenv("QUEUE_NAME")

API_V1_STR: str = "/api/v1"

DATABASE_URL = os.getenv(
    "DB_HOST",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
)  # connect string for the real database