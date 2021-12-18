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

__all__ = ["Polaris"]

import asyncio
import typing as t
import logging

import aioredis
import hikari
import lightbulb
import orjson

from . import messages

_LOGGER = logging.getLogger("lightbulb.ext.polaris")
MessageHandlerT = t.Callable[[messages.Message], t.Coroutine[t.Any, t.Any, None]]


class Polaris:
    __slots__ = ("_app", "_redis_url", "_redis_cli", "_poll_task", "_handlers", "_fallback_handler")

    def __init__(self, app: lightbulb.BotApp, redis_url: str):
        self._app: lightbulb.BotApp = app
        self._redis_url: str = redis_url
        self._redis_cli: aioredis.Redis = aioredis.from_url(self._redis_url)
        self._poll_task: t.Optional[asyncio.Task[None]] = None

        self._handlers: t.Dict[t.Tuple[messages.MessageType, str], MessageHandlerT] = {}
        self._fallback_handler: t.Optional[MessageHandlerT] = None

        self._app.subscribe(lightbulb.LightbulbStartedEvent, self.run)
        self._app.subscribe(hikari.StoppingEvent, self.close)

    async def _poll(self) -> t.AsyncIterator[bytes]:
        while True:
            async with self._redis_cli as r:
                out = await r.brpop("polaris-mq", 0)
                yield out[1]

    async def _handle_messages(self) -> None:
        async for raw_message in self._poll():
            message = messages.Message.from_json(orjson.loads(raw_message))
            _LOGGER.debug("Received message: %s (%s)", message.name, message.type)
            handler = self._handlers.get((message.type, message.name))
            if handler is None:
                handler = self._fallback_handler

            if handler is not None:
                await handler(message)

    async def run(self, _: lightbulb.LightbulbStartedEvent) -> None:
        _LOGGER.info("Listening for messages")
        self._poll_task = asyncio.create_task(self._handle_messages())

    async def close(self, _: hikari.StoppingEvent) -> None:
        if self._poll_task is not None:
            self._poll_task.cancel()
        await self._redis_cli.close()

    def add_handler_for(self, message_name: str, message_types: t.Union[messages.MessageType, t.Sequence[messages.MessageType]], handler_func: MessageHandlerT):
        if isinstance(message_types, messages.MessageType):
            message_types = [message_types]

        for m_type in message_types:
            self._handlers[(m_type, message_name)] = handler_func

    def handler_for(self, message_name: str, message_types: t.Union[messages.MessageType, t.Sequence[messages.MessageType]]):
        def decorate(handler_func: MessageHandlerT) -> MessageHandlerT:
            nonlocal message_name, message_types

            if isinstance(message_types, messages.MessageType):
                message_types = [message_types]

            for m_type in message_types:
                self._handlers[(m_type, message_name)] = handler_func
            return handler_func
        return decorate
