from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

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
    """Logs outbound messages — real SMTP/Twilio/webhooks require credentials."""

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


class NotificationService:
    def __init__(self) -> None:
        self._adapters: dict[NotificationChannel, ChannelAdapter] = {
            NotificationChannel.IN_APP: InAppAdapter(),
            NotificationChannel.EMAIL: StubChannelAdapter(NotificationChannel.EMAIL),
            NotificationChannel.SMS: StubChannelAdapter(NotificationChannel.SMS),
            NotificationChannel.TEAMS: StubChannelAdapter(NotificationChannel.TEAMS),
            NotificationChannel.SLACK: StubChannelAdapter(NotificationChannel.SLACK),
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
