import os
import asyncio
import aio_pika
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aio_pika import Message, DeliveryMode
from aio_pika.exceptions import AMQPConnectionError

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")


async def send_email(subject: str, to_email: str, body: str):
    """
    Отправка email через SMTP сервер
    """
    sender_email = "14db251f6060e2"
    sender_password = "5f6f0551c4af30"
    smtp_server = "sandbox.smtp.mailtrap.io"
    smtp_port = 587

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Начинаем защищенное соединение
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


async def on_message(message: aio_pika.IncomingMessage):
    """
    Обработчик для сообщений из RabbitMQ
    """
    async with message.process():
        try:
            # Декодируем сообщение и обрабатываем его
            email_data = message.body.decode()
            print(f"Received message: {email_data}")
            # Предположим, что message содержит данные для отправки email
            subject = "Test Email"
            to_email = "recipient@example.com"
            body = email_data

            # Отправка email
            await send_email(subject, to_email, body)
        except Exception as e:
            print(f"Error processing message: {e}")


async def main():
    """
    Главная функция для подключения к RabbitMQ и подписки на очередь
    """
    connection = None
    channel = None

    while True:
        try:
            # Подключаемся к RabbitMQ
            print("Connecting to RabbitMQ...")
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            print("Connected to RabbitMQ")

            # Подписываемся на очередь
            queue = await channel.declare_queue("email_queue", durable=True)
            await queue.consume(on_message, no_ack=False)

            print("Waiting for messages...")
            await asyncio.Future()  # Ожидаем бесконечно
        except AMQPConnectionError as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            if connection:
                await connection.close()
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
