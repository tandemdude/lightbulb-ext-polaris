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

import dataclasses
import enum


class MessageType(enum.IntEnum):
    CREATE = 0
    READ = 1
    UPDATE = 2
    DELETE = 3


@dataclasses.dataclass
class Message:
    type: MessageType
    name: str
    data: dict

    @classmethod
    def from_json(cls, payload: dict):
        return cls(
            MessageType(payload["type"]),
            payload["name"],
            payload.get("data", {})
        )

    async def respond(self, *args, **kwargs):
        raise NotImplementedError
