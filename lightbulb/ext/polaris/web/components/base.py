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

__all__ = ["Renderable", "ComponentGroup"]

import abc
import inspect
import typing as t

from jinja2 import Environment
from jinja2 import BaseLoader


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


class ComponentGroup(Renderable, abc.ABC):
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
