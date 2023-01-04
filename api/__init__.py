"""
Abstract base class and helper classes for the server-proivded REST API

Overview
--------

During the marsheling of client requests (provided by the `urest.http.server.RESTServer`
class), the path portion of the URI is extracted from the client. This path is
expected to take the form of

> `/ noun / verb`

The 'noun' determines the resource of the request, and the 'verb' the action to
be taken on that resource. Also important is the intent of the client as
inferred from the underlying HTTP request, e.g. `GET` or `PUT`. Taken together
the URI and the client intent are mapped as follows


Implementation
--------------



Using the Module
----------------


Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W

Licence
-------

This module, and all included code, is made available under the terms of the MIT Licence

> Copyright (c) 2022--2023 David Love

> Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

> The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

### Expose the `http` module interface
from .base import APIBase
