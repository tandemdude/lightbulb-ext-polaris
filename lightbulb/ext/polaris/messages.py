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

__all__ = ["MessageType", "Message"]

import typing as t
import dataclasses
import enum


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


@dataclasses.dataclass
class Message:
    """
    Dataclass representing a message received from polaris' redis
    message queue.
    """
    id: str
    """The unique ID of this message."""
    type: MessageType
    """The type of this message."""
    name: str
    """The name of this message."""
    data: dict
    """The associated data payload for this message."""

    def __repr__(self) -> str:
        return f"Message(id={self.id}, type={self.type}, name={self.name})"

    @classmethod
    def from_json(cls, payload: dict) -> Message:
        """
        Create a Message object from a raw message payload.

        Args:
            payload (:obj:`dict`): Paylod to create the Message object from.
        """
        return cls(
            payload["id"],
            MessageType(payload["type"]),
            payload["name"],
            payload.get("data", {})
        )

    async def respond(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise NotImplementedError
