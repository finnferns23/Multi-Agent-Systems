from __future__ import annotations

import os
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PushNotificationInput(BaseModel):
    """Input schema for the push notification tool."""

    message: str = Field(..., description="Message to send to the user.")


class PushNotificationTool(BaseTool):
    name: str = "Send Push Notification"
    description: str = (
        "Send a push notification to the user using Pushover when PUSHOVER_USER and PUSHOVER_TOKEN are configured."
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message: str) -> str:
        pushover_user = os.getenv("PUSHOVER_USER")
        pushover_token = os.getenv("PUSHOVER_TOKEN")

        if not pushover_user or not pushover_token:
            return '{"notification": "skipped", "reason": "Pushover credentials not configured"}'

        payload = {
            "user": pushover_user,
            "token": pushover_token,
            "message": message,
        }

        try:
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data=payload,
                timeout=20,
            )
            response.raise_for_status()
            return '{"notification": "sent"}'
        except requests.RequestException as exc:
            return f'{{"notification": "failed", "error": "{str(exc)}"}}'
