import os
from html import escape

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType


load_dotenv()


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Contacts API"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "True").lower() == "true",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "True").lower() == "true",
)


async def send_verification_email(
    email: str,
    username: str,
    verification_url: str,
) -> None:
    html = f"""
    <html>
        <body>
            <h2>Hello, {escape(username)}!</h2>
            <p>Thank you for registering in Contacts API.</p>
            <p>Please confirm your email address by clicking the link below:</p>
            <p>
                <a href="{escape(verification_url, quote=True)}">
                    Confirm email
                </a>
            </p>
            <p>If you did not create this account, please ignore this email.</p>
        </body>
    </html>
    """


    message = MessageSchema(
        subject="Confirm your email address",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )

    mail=FastMail(conf)
    await mail.send_message(message)