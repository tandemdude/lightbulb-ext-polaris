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

__all__ = ["Body", "Page", "Paragraph", "Div"]

import abc
import typing as t

from . import base
from . import utils


class Paragraph(base.Renderable, abc.ABC):
    html = """<p class="{{ classes }}">{{ content }}</p>"""

    @property
    def content(self) -> t.Union[str, base.Renderable]:
        return "Hello World!"

    def render(self, **kwargs) -> str:
        content = self.content
        if isinstance(content, base.Renderable):
            content = content.render(**kwargs)

        return self._render(
            Paragraph.html,
            classes=utils.to_cls_string(self.classes),
            content=content,
            **kwargs,
        )


class Div(base.ComponentGroup):
    html = """
    <div class="{{ classes }}">
        {{ inner }}
    </div>
    """

    def render(self, **kwargs) -> str:
        out = super().render(**kwargs)
        return self._render(
            Div.html,
            inner=out,
            classes=utils.to_cls_string(self.classes),
            **kwargs,
        )


class Body(base.ComponentGroup):
    html = """
    <body class="{{ classes }}">
        {{ inner }}
    </body>
    """

    def render(self, **kwargs) -> str:
        out = super().render(**kwargs)
        return self._render(
            Body.html,
            classes=utils.to_cls_string(self.classes),
            inner=out,
            **kwargs,
        )


class Page(base.Renderable):
    html = """
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }}</title>
        <link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet">
    </head>
    {{ body }}
    </html>
    """

    def __init__(self, title: str, body: t.Optional[base.Renderable] = None) -> None:
        self.title = title
        self.body = body or Body()

    def render(self, **kwargs) -> str:
        return self._render(
            Page.html,
            title=self.title,
            body=self.body.render(**kwargs),
            **kwargs,
        )
