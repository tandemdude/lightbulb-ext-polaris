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

__all__ = ["Renderable", "Body", "Page", "Paragraph", "Grid"]

import functools
import abc
import typing as t
import inspect

from jinja2 import Environment
from jinja2 import BaseLoader


def _to_cls_string(classes: t.Union[str, t.Iterable[str]]):
    return classes if isinstance(classes, str) else " ".join(classes)


class Renderable(abc.ABC):
    _ENVIRON = Environment(loader=BaseLoader())

    @property
    def classes(self) -> t.Union[str, t.Iterable[str]]:
        return ""

    def _render(self, template_str: str, **kwargs) -> str:
        return self._ENVIRON.from_string(template_str.strip()).render(**kwargs)

    @abc.abstractmethod
    def render(self, **kwargs) -> str:
        ...


class ComponentGroup(Renderable):
    html = """
    {% for component in components %}
        {{ component.render(**_extras) }}
    {% endfor %}
    """

    def __init__(self):
        self.components = []

        items = [*self.__class__.__dict__.values(), *self.__dict__.values()]
        for item in items:
            if isinstance(item, Renderable):
                self.components.append(item)
            elif inspect.isclass(item) and issubclass(item, Renderable):
                self.components.append(item())

    def render(self, **kwargs) -> str:
        return self._render(
            ComponentGroup.html,
            components=self.components,
            _extras=kwargs,
            **kwargs,
        )


class Paragraph(Renderable, abc.ABC):
    html = """<p class="{{ classes }}">{{ content }}</p>"""

    @property
    def content(self) -> t.Union[str, Renderable]:
        return "Hello World!"

    def render(self, **kwargs) -> str:
        content = self.content
        if isinstance(content, Renderable):
            content = content.render(**kwargs)

        return self._render(
            Paragraph.html,
            classes=_to_cls_string(self.classes),
            content=content,
            **kwargs,
        )


class Grid(ComponentGroup):
    html = """
    <div class="grid grid-cols-{{columns}} {{ classes }}">
        {{ inner }}
    </div>
    """

    @property
    def columns(self) -> int:
        return 3

    def render(self, **kwargs) -> str:
        out = super().render(**kwargs)
        return self._render(
            Grid.html,
            inner=out,
            classes=_to_cls_string(self.classes),
            columns=self.columns,
            **kwargs,
        )


class Body(ComponentGroup):
    html = """
    <body class="{{ classes }}">
        {{ inner }}
    </body>
    """

    def render(self, **kwargs) -> str:
        out = super().render(**kwargs)
        return self._render(
            Body.html,
            classes=_to_cls_string(self.classes),
            inner=out,
            **kwargs,
        )


class Page(Renderable):
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

    def __init__(self, title: str, body: t.Optional[Renderable] = None) -> None:
        self.title = title
        self.body = body or Body()

    def render(self, **kwargs) -> str:
        return self._render(
            Page.html,
            title=self.title,
            body=self.body.render(**kwargs),
            **kwargs,
        )
