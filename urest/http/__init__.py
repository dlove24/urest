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

"""
Network interface and helper classes for abstracting the underlying HTTP stream.
This module provides the abstraction of the underlying socket handling code,
using in marshaling requests from clients and building the response. All the
socket handling is built around the Python 3 `asyncio` library for the low-level
network interface, and for the use of co-routines to simplify request handling.

In most cases, consumers of this module only need to provide an `asynio` event
loop: see "Creating the Network Server" in the Section _Using the Module_ below.
By default the module will also bind to the _network_ address of the host on the
standard port 80 used by HTTP requests. This can be changed in the instantiation
of the  `urest.http.server.RESTServer` class.

Implementation
--------------

During the instantiation of the `urest.http.server.RESTServer` class, the resulting
object creates a socket bound to the specified address and port (or the host network
address and port 80 by default). This binding is undertaken as part of the `asyncio`


Using the Module
----------------

### Creating the Network Server

All network clients are assumed to be handled by an instance of the
`urest.http.server.RESTServer` class from the `urest.http.server` module. The
`urest.http.server.RESTServer` class provides both an event loop for the
`asyncio` library, and also takes care of the lower-level networking interface
for the clients. Unless working with multiple instances (e.g. via a thread
library), most model consumers are assumed have a single instance of the
`urest.http.server.RESTServer` --- **but the module will not check this**.

In most cases, something similar to the following will suffice

```python
  # Import the Asynchronous IO Library
  try:
    import uasyncio as asyncio
  except ImportError:
    import asyncio

  from urest.http import RESTServer

  app = RESTServer()

  if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
```

.. Warning::

  There is no guarantee of thread-safety in this module, and all
  'concurrency' is assumed to be via co-routines provided by the `asyncio`
  library. For an overview of how multiple clients can be handled using
  co-routines, [Async IO in Python](https://realpython.com/async-io-python) is
  highly recommended reading.

### Creating the API Responses

Most module consumers will not use the `urest.http.response` module directly:
but will instead sub-class `urest.api.base.APIBase` to provide the core of the
response to the network clients. For details of how the `urest.http.server.RESTServer` and `urest.api.base.APIBase` classes interact, the module documentation for `urest.api` should be consulted. In addition, the documentation for the `urest.examples.simpleled.SimpleLED` class might prove useful as an example of a simple implementation of the API.


Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W


"""

### Expose the `http` module interface
from .server import RESTServer
from .response import HTTPResponse
