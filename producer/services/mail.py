import json

import aio_pika
from aio_pika import channel

import settings

async def send_message(message, channel1: channel):
    message = json.dumps(message)
    try:
        print(f"Publishing message to queue {settings.QUEUE_NAME}: {message}")
        await channel1.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Сообщения будут сохранены на диске
            ),
            routing_key=settings.QUEUE_NAME,
        )
        return {"status": "success", "message": "Message published to RabbitMQ"}
    except Exception as e:
        print(f"Failed to publish message: {e}")
        raise Exception(e)
