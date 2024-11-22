import json

from email_validator import TEST_ENVIRONMENT
from fastapi import FastAPI, HTTPException, Depends, status
import aio_pika
import os
import asyncio

from pydantic import BaseModel, EmailStr

app = FastAPI()

# Читаем параметры подключения к RabbitMQ из переменных окружения
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
QUEUE_NAME = "email_queue"

# Глобальная переменная для подключения к RabbitMQ
connection = None
channel = None


@app.on_event("startup")
async def startup_event():
    """
    Инициализация подключения к RabbitMQ при старте приложения.
    """
    global connection, channel
    try:
        print("Connecting to RabbitMQ...")
        print('!!!!!! 1')
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        print('!!!!!! 2')
        await channel.declare_queue(QUEUE_NAME, durable=True)
        print("Connected to RabbitMQ.")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Закрытие подключения к RabbitMQ при остановке приложения.
    """
    global connection
    if connection:
        await connection.close()
        print("RabbitMQ connection closed.")


# Модель данных для email
class EmailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    body: str


TEST_API_KEYS = {"your-api-key-12345"}

def authenticate(api_key: str):
    if api_key not in TEST_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


@app.post("/send-email/")
async def send_email_message(email: EmailSchema, api_key: str = Depends(authenticate)):
    """
    Публикует сообщение в очередь RabbitMQ.
    """
    message = email.dict()
    message = json.dumps(message)

    try:
        print(f"Publishing message to queue {QUEUE_NAME}: {message}")
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Сообщения будут сохранены на диске
            ),
            routing_key=QUEUE_NAME,
        )
        return {"status": "success", "message": "Message published to RabbitMQ"}
    except Exception as e:
        print(f"Failed to publish message: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish message")


@app.get("/")
async def read_root():
    """
    Тестовый маршрут для проверки работы сервера.
    """
    return {"message": "RabbitMQ Publisher is running."}
