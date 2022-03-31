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

__all__ = ["Client", "BotClient"]

import asyncio
import logging
import typing as t

import aioredis
import hikari
import orjson

from . import messages

_LOGGER = logging.getLogger("lightbulb.ext.polaris")
MessageHandlerT = t.Callable[[messages.Message], t.Coroutine[t.Any, t.Any, None]]


class Client:
    __slots__ = ("_redis_url", "_queue_name", "_resp_expire", "_redis_cli")

    def __init__(self, redis_url: str, queue_name: str = "polaris", resp_expire: int = 15 * 60) -> None:
        self._redis_url: str = redis_url
        self._queue_name: str = queue_name
        self._resp_expire: int = resp_expire
        self._redis_cli: aioredis.Redis = aioredis.from_url(self._redis_url)

        messages.Message._polaris = self
        messages.Response._polaris = self

    async def send_message(self, msg: messages.Message, wait_for_response: bool = False) -> t.Optional[messages.Response]:
        payload = orjson.dumps(msg.to_json())
        await self._redis_cli.lpush(f"{self._queue_name}-mq", payload)

        if wait_for_response:
            return await self.wait_for_response(msg.id)

    async def send_response(self, resp: messages.Response) -> None:
        payload = orjson.dumps(resp.to_json())
        await self._redis_cli.lpush(resp.id, payload)
        await self._redis_cli.expire(resp.id, self._resp_expire)

    async def wait_for_response(self, id: str) -> messages.Response:
        async with self._redis_cli as r:
            out = await r.brpop(id, 0)
        return messages.Response.from_json(orjson.loads(out))

    async def close(self) -> None:
        await self._redis_cli.close()


class BotClient(Client):
    __slots__ = ("_app", "_poll_task", "_handlers", "_fallback_handler", "_resp_expire", "_running")

    def __init__(self, app: hikari.GatewayBot, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._app: hikari.GatewayBot = app
        self._running: bool = False
        self._poll_task: t.Optional[asyncio.Task[None]] = None

        self._handlers: t.Dict[t.Tuple[messages.MessageType, str], MessageHandlerT] = {}
        self._fallback_handler: t.Optional[MessageHandlerT] = None

        self._app.subscribe(hikari.StartedEvent, self._run)
        self._app.subscribe(hikari.StoppingEvent, self._close)

    async def _poll(self) -> t.AsyncIterator[bytes]:
        while True:
            async with self._redis_cli as r:
                out = await r.brpop(f"{self._queue_name}-mq", 0)
                yield out[1]

    async def _handle_messages(self) -> None:
        async for raw_message in self._poll():
            message = messages.Message.from_json(orjson.loads(raw_message))
            _LOGGER.debug("Received message: %s (%s)", message.name, message.type)
            handler = self._handlers.get((message.type, message.name))
            if handler is None:
                handler = self._fallback_handler

            if handler is not None:
                asyncio.create_task(handler(message))
            else:
                _LOGGER.warning("Discarding message: %s (%s) as no handler was found", message.name, message.type)

    async def _run(self, _: hikari.StartedEvent) -> None:
        await self.run()

    async def run(self) -> None:
        if not self._running:
            _LOGGER.info("Listening for messages")
            self._poll_task = asyncio.create_task(self._handle_messages())
            self._running = True

    async def _close(self, _: hikari.StoppingEvent) -> None:
        await self.close()

    async def close(self) -> None:
        if self._poll_task is not None:
            self._poll_task.cancel()
        if self._running:
            await super().close()
            self._running = False

    def add_handler_for(
        self,
        message_name: str,
        message_types: t.Union[messages.MessageType, t.Sequence[messages.MessageType]],
        handler_func: MessageHandlerT,
    ) -> None:
        """
        Method to register a function as a message handler for messages with the given name
        and given type(s).

        Args:
            message_name (:obj:`str`): Name of the message that this handler function is for.
            message_types (Union[:obj:`~.messages.MessageType`, Sequence[:obj:`~.messages.MessageType`]]): The message
                type(s) that this handler will be called for.
            handler_func: Function to register as a message handler.

        Returns:
            ``None``
        """
        if isinstance(message_types, messages.MessageType):
            message_types = [message_types]

        for m_type in message_types:
            self._handlers[(m_type, message_name)] = handler_func

    def handler_for(
        self, message_name: str, message_types: t.Union[messages.MessageType, t.Sequence[messages.MessageType]]
    ) -> t.Callable[[MessageHandlerT], MessageHandlerT]:
        """
        Second order decorator to register a function as a message handler for messages with the given name
        and given type(s).

        Args:
            message_name (:obj:`str`): Name of the message that this handler function is for.
            message_types (Union[:obj:`~.messages.MessageType`, Sequence[:obj:`~.messages.MessageType`]]): The message
                type(s) that this handler will be called for.
        """
        def decorate(handler_func: MessageHandlerT) -> MessageHandlerT:
            nonlocal message_name, message_types

            if isinstance(message_types, messages.MessageType):
                message_types = [message_types]

            for m_type in message_types:
                self._handlers[(m_type, message_name)] = handler_func
            return handler_func

        return decorate

    @t.overload
    def set_default_handler(self) -> t.Callable[[MessageHandlerT], MessageHandlerT]:
        ...

    @t.overload
    def set_default_handler(self, handler_func: MessageHandlerT) -> MessageHandlerT:
        ...

    def set_default_handler(
        self, handler_func: t.Optional[MessageHandlerT] = None
    ) -> t.Union[MessageHandlerT, t.Callable[[MessageHandlerT], MessageHandlerT]]:
        """
        Set the default message handler function to the given function. This method can be used as a
        first or second order decorator, or called with the function to set the default handler to.
        """
        if handler_func is not None:
            self._fallback_handler = handler_func
            return handler_func

        def decorate(handler_func_: MessageHandlerT) -> MessageHandlerT:
            self._fallback_handler = handler_func_
            return handler_func_

        return decorate
