import json
import aio_pika

from http.client import HTTPException

from fastapi import FastAPI, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

import settings
from db.models import ClientApp

from schemas.messages import EmailSchema

from services.auth import authenticate


app = FastAPI(title="service mail-sender")

root_router = APIRouter()
app.include_router(root_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ping/")
async def ping(client_app: ClientApp = Depends(authenticate)):
    return client_app


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
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        channel = await connection.channel()

        await channel.declare_queue(settings.QUEUE_NAME, durable=True)
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


@app.post("/send-email/")
async def send_email_message(email: EmailSchema, client_app: ClientApp = Depends(authenticate)):
    """
    Публикует сообщение в очередь RabbitMQ.
    """
    global connection
    message = email.dict()
    message = json.dumps(message)
    try:
        print(f"Publishing message to queue {settings.QUEUE_NAME}: {message}")
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Сообщения будут сохранены на диске
            ),
            routing_key=settings.QUEUE_NAME,
        )
        return {"status": "success", "message": "Message published to RabbitMQ"}
    except Exception as e:
        print(f"Failed to publish message: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish message")
