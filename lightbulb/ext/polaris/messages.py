# -*- coding: utf-8 -*-
# Copyright © tandemdude 2021-present
#
# This file is part of lightbulb-ext-polaris.
#
# Lightbulb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lightbulb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Lightbulb. If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

__all__ = ["MessageType", "Response", "Message"]

import enum
import typing as t
import uuid

if t.TYPE_CHECKING:
    from . import client


class MessageType(enum.IntEnum):
    """
    Enum representing the type of the given polaris message.
    """

    CREATE = 0
    """A create operation."""
    READ = 1
    """A read operation. (this may be removed)"""
    UPDATE = 2
    """An update (edit) operation."""
    DELETE = 3
    """A delete operation."""


class Response:
    _polaris: t.Optional[client.Polaris] = None
    __slots__ = ("id", "data")

    def __init__(self, id: str, data: dict) -> None:
        self.id = id
        """The unique ID of the message that this response is for."""
        self.data = data
        """The associated data payload for this response."""

    def __repr__(self) -> str:
        return f"Response(id={self.id})"

    @classmethod
    def from_json(cls, payload: dict) -> Response:
        """
        Create a Message object from a raw message payload.

        Args:
            payload (:obj:`dict`): Payload to create the Message object from.
        """
        return cls(payload["id"], payload.get("data", {}))

    def to_json(self) -> dict:
        """
        Create a raw message payload from this Message object.
        """
        return {"id": self.id, "data": self.data}


class Message:
    """
    Class representing a message received from polaris' redis
    message queue.
    """

    _polaris: t.Optional[client.Polaris] = None
    __slots__ = ("id", "type", "name", "data")

    def __init__(self, type_: MessageType, name: str, data: dict, id_: t.Optional[str] = None) -> None:
        self.type: MessageType = type_
        """The type of this message."""
        self.name: str = name
        """The name of this message."""
        self.data: dict = data
        """The associated data payload for this message."""
        self.id: str = id_ if id_ is not None else str(uuid.uuid4())
        """The unique ID of this message."""

    def __repr__(self) -> str:
        return f"Message(id={self.id}, type={self.type}, name={self.name})"

    @classmethod
    def from_json(cls, payload: dict) -> Message:
        """
        Create a Message object from a raw message payload.

        Args:
            payload (:obj:`dict`): Payload to create the Message object from.
        """
        return cls(MessageType(payload["type"]), payload["name"], payload.get("data", {}), payload["id"])

    def to_json(self) -> dict:
        """
        Create a raw message payload from this Message object.
        """
        return {"id": self.id, "type": int(self.type), "name": self.name, "data": self.data}

    async def respond(self, data: t.Optional[dict] = None) -> Response:
        """
        Send a response to this message.

        Args:
            data (Optional[:obj:`dict`]): Data to include with the response.

        Returns:
            :obj:`~Response`: The created response.
        """
        assert Message._polaris is not None
        resp = Response(self.id, data or {})
        await Message._polaris.send_response(resp)
        return resp
