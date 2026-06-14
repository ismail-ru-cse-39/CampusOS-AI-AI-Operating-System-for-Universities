from __future__ import annotations

import asyncio
import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    TEAMS = "teams"
    SLACK = "slack"
    IN_APP = "in_app"


@dataclass
class NotificationMessage:
    id: UUID
    user_id: str
    channel: NotificationChannel
    subject: str
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "queued"


class ChannelAdapter(ABC):
    channel: NotificationChannel

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        ...


class InAppAdapter(ChannelAdapter):
    channel = NotificationChannel.IN_APP

    def __init__(self) -> None:
        self._inbox: list[NotificationMessage] = []

    async def send(self, message: NotificationMessage) -> bool:
        message.status = "delivered"
        self._inbox.append(message)
        return True

    def get_inbox(self, user_id: str) -> list[NotificationMessage]:
        return [m for m in self._inbox if m.user_id == user_id]


class StubChannelAdapter(ChannelAdapter):
    """Logs outbound messages when channel credentials are not configured."""

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel

    async def send(self, message: NotificationMessage) -> bool:
        logger.info(
            "notification_stub channel=%s user=%s subject=%s",
            self.channel.value,
            message.user_id,
            message.subject,
        )
        message.status = "stub_delivered"
        return True


class EmailAdapter(ChannelAdapter):
    channel = NotificationChannel.EMAIL

    async def send(self, message: NotificationMessage) -> bool:
        if not settings.smtp_configured:
            return await StubChannelAdapter(NotificationChannel.EMAIL).send(message)

        def _send_sync() -> None:
            email = EmailMessage()
            email["Subject"] = message.subject
            email["From"] = settings.smtp_from
            email["To"] = message.metadata.get("email", message.user_id)
            email.set_content(message.body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(email)

        try:
            await asyncio.to_thread(_send_sync)
            message.status = "delivered"
            return True
        except Exception as exc:
            logger.error("email_send_failed user=%s error=%s", message.user_id, exc)
            message.status = "failed"
            return False


class SMSAdapter(ChannelAdapter):
    channel = NotificationChannel.SMS

    async def send(self, message: NotificationMessage) -> bool:
        if not settings.twilio_configured:
            return await StubChannelAdapter(NotificationChannel.SMS).send(message)

        phone = message.metadata.get("phone", message.user_id)
        url = (
            f"https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.twilio_account_sid}/Messages.json"
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    auth=(settings.twilio_account_sid, settings.twilio_auth_token),
                    data={
                        "From": settings.twilio_from_number,
                        "To": phone,
                        "Body": f"{message.subject}: {message.body}",
                    },
                )
                response.raise_for_status()
            message.status = "delivered"
            return True
        except Exception as exc:
            logger.error("sms_send_failed user=%s error=%s", message.user_id, exc)
            message.status = "failed"
            return False


class WebhookAdapter(ChannelAdapter):
    def __init__(self, channel: NotificationChannel, webhook_url: str) -> None:
        self.channel = channel
        self.webhook_url = webhook_url

    async def send(self, message: NotificationMessage) -> bool:
        if not self.webhook_url:
            return await StubChannelAdapter(self.channel).send(message)

        payload = {
            "text": f"*{message.subject}*\n{message.body}",
            "subject": message.subject,
            "body": message.body,
            "user_id": message.user_id,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
            message.status = "delivered"
            return True
        except Exception as exc:
            logger.error("webhook_send_failed channel=%s error=%s", self.channel.value, exc)
            message.status = "failed"
            return False


class NotificationService:
    def __init__(self) -> None:
        self._adapters: dict[NotificationChannel, ChannelAdapter] = {
            NotificationChannel.IN_APP: InAppAdapter(),
            NotificationChannel.EMAIL: EmailAdapter(),
            NotificationChannel.SMS: SMSAdapter(),
            NotificationChannel.TEAMS: WebhookAdapter(
                NotificationChannel.TEAMS, settings.teams_webhook_url
            ),
            NotificationChannel.SLACK: WebhookAdapter(
                NotificationChannel.SLACK, settings.slack_webhook_url
            ),
        }

    async def notify(
        self,
        *,
        user_id: str,
        channel: NotificationChannel,
        subject: str,
        body: str,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationMessage:
        message = NotificationMessage(
            id=uuid4(),
            user_id=user_id,
            channel=channel,
            subject=subject,
            body=body,
            metadata=metadata or {},
        )
        adapter = self._adapters.get(channel)
        if adapter is None:
            message.status = "failed"
            return message
        await adapter.send(message)
        return message

    async def notify_at_risk_alert(self, student_name: str, advisor_id: str) -> NotificationMessage:
        return await self.notify(
            user_id=advisor_id,
            channel=NotificationChannel.IN_APP,
            subject=f"At-risk alert: {student_name}",
            body=f"{student_name} has been flagged for retention intervention.",
            metadata={"type": "at_risk_alert"},
        )

    def get_in_app_messages(self, user_id: str) -> list[NotificationMessage]:
        adapter = self._adapters[NotificationChannel.IN_APP]
        if isinstance(adapter, InAppAdapter):
            return adapter.get_inbox(user_id)
        return []


notification_service = NotificationService()
