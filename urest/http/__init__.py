# This module, and all included code, is made available under the terms of the MIT Licence
#
# Copyright 2021--2022 (c) Erik de Lange, Copyright (c) 2022--2023 David Love
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""The internal network interface and helper classes for abstracting the
underlying HTTP stream live in the `http` package. When creating an API using
the `urest` library, the `http` package provides the abstraction of the
underlying socket handling code. Specifically all marshaling requests from the
network clients, calling of the library users API classes, and responses to the
network clients passes through the `http` package. All low-level code for the
socket handling in `http` is built around the Python 3 `asyncio` library, and
the library user API is similarly expected to be based around the use of co-
routines to simplify request handling.

In most cases, library users only need to provide an `asynio` event loop, and the
bind the [`RESTServer`][urest.http.server.RESTServer] from the `http` module to
that loop. See the _HOW-TO_ "_Creating a Network Server_" for more details. By
default the module will also bind to the _network_ address of the host on the
standard port 80 used by HTTP requests. This can be changed in the instantiation of
the  [`RESTServer`][urest.http.server.RESTServer] class, and before binding to the
`asyncio` loop.

Package and Class Layout
--------------

![Package Layout for urest.http](/media/urest_http.svg)


Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W
"""

### Expose the `http` module interface
from .response import HTTPResponse
from .server import RESTServer
