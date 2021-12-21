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

__all__ = ["BodyWithSidebar"]

from .. import basic


class BodyWithSidebar(basic.Body):
    classes = "grid grid-cols-5 bg-gray-300 font-mono"

    class Sidebar(basic.Div):
        classes = "col-span-1 bg-gray-800"

        class P1(basic.Paragraph):
            content = "Some Text"
            classes = "mt-10 text-center text-gray-200 text-2xl"

    class Content(basic.Div):
        classes = "col-span-4"

        class P2(basic.Paragraph):
            content = "Some More Text"
            classes = "text-center mt-10 text-2xl text-gray-800"
