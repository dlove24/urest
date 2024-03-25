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
that loop. The internal details of the `http` module are not needed in most
use-cases: see the [Creating a Network Server][creating-a-network-server] How-
To_for more details.

By default the module will also bind to the _network_ address of the host on the
standard port 80 used by HTTP requests. This can be changed in the instantiation of
the [`RESTServer`][urest.http.server.RESTServer] class, and before binding to the
`asyncio` loop.

## Package and Class Layout

The core classes of the `HTTP` module are organised as follows. In most cases only
the [`RESTServer`][urest.http.server.RESTServer] class will be directly used by
library users.

![Package Layout for urest.http](../media/urest_http.svg)

## Example Implementation

### Getting the Noun State

This example is based on the [`SimpleLED`][urest.examples.simpleled.SimpleLED]
class as a minimal implementation of a noun controlling a GPIO pin, using the
MicroPython `Pin` library. The full documentation for an example based on the
[`SimpleLED`][urest.examples.simpleled.SimpleLED] class is available through the
`urest.examples` package. Details of the calls needed to set-up the [`RESTServer`][urest.http.server.RESTServer] are also provided in the [_Creating a Network Server_][creating-a-network-server] How-To.

The following sequence diagrams assume that a [`RESTServer`][urest.http.server.RESTServer]
has been created as

```python
app = RESTServer()
```

and the [`SimpleLED`][urest.examples.simpleled.SimpleLED] class subsequently registred as the 'noun' `led` via the [`RESTServer.register_noun()`][urest.http.server.RESTServer.register_noun] method as

```python
app.register_noun('led', SimpleLED(28))
```

The calling application then hands over to the `app` instance (of the [`RESTServer`][urest.http.server.RESTServer]) class via the [`start()`][urest.http.server.RESTServer.start] method of the `app` instance

```python
  if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
```

Subsequently a client on the network wants to query the state of the `led`
via the HTTP request to the server

```
GET /led HTTP 1.1
```

On receiving the above request from the client, the [`RESTServer`][urest.http.server.RESTServer] instance will call the relevant methods of the [`SimpleLED`][urest.examples.simpleled.SimpleLED] (as a sub-class of [`APIBase`][urest.api.base.APIBase]) as shown in Figure 1. Note that the '`<< resource state>>`' returned by [`SimpleLED.get_state()`] [urest.examples.simpleled.SimpleLED] is as a Python `dict[str, Union[str, int]]`. The `<< headers >>` are also assumed to follow the [HTTP/1.1 specification](https://www.ietf.org/rfc/rfc2616.txt); whether read from the HTTP response itself, or stored internally by [`HTTPResponse`] [urest.http.response.HTTPResponse].

![Figure 1: A Sequence Diagram for the Noun Get Request](../media/sd_http_get.svg)

**Figure 1: A Sequence Diagram for the Noun Get Request of the Example**

The initial network request from the client is handled by the event loop of the
`asyncio` library, which will create instances of
[`asyncio.StreamReader`](https://docs.python.org/3.4/library/asyncio-stream.html#streamreader)
and
[`asyncio.StreamWriter`](https://docs.python.org/3.4/library/asyncio-stream.html#streamwriter)
to represent data being read from, or written to, the network respectively. Once
this is done, the `asyncio` library will call
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] to
handle the request.

The [`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun],
in turn, creates an instances of the [`HTTPResponse`]
[urest.http.response.HTTPResponse] class. This instance of [`HTTPResponse`]
[urest.http.response.HTTPResponse] is then set-up from the data read from the
HTTP headers via the
[`asyncio.StreamReader`](https://docs.python.org/3.4/library/asyncio-stream.html#streamreader).

With the inital set-up complete,
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] calls
the relevant handler for the request. In this example [`SimpleLED.get_state()`]
[urest.examples.simpleled.SimpleLED] from an instance of
[`SimpleLED`][urest.examples.simpleled.SimpleLED] set-up earlier.

Once the [`SimpleLED.get_state()`][urest.examples.simpleled.SimpleLED] method
completes, the returned data is parsed by the
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun].
Valid responses from the [`SimpleLED.get_state()`]
[urest.examples.simpleled.SimpleLED] method are then used to complete the set-up
of the [`HTTPResponse`][urest.http.response.HTTPResponse] instance. Finally
[`HTTPResponse.send()`][urest.http.response.HTTPResponse.send] is called to
return the data to the client via the
[`asyncio.StreamWriter`](https://docs.python.org/3.4/library/asyncio-stream.html#streamwriter).

### Setting the Noun State

Setting the state of the noun is a little more involved on the client side, as
this will require the desired state of the noun to be sent to the server. A useful
tool for testing purposes is the [curl](https://curl.se) utility; available on
most platforms.

Continuing the minimal example above, the command line

```
curl -X PUT -d '{"led":"0"}' -H "Content-Type: application/json" http://10.0.30.225/LED
```

will transmit something like the following HTTP request to
[`RESTServer`][urest.http.server.RESTServer]

```
PUT /LED HTTP/1.1

Host: 10.0.30.225
User-Agent: curl/7.81.0
Accept: */*
Content-Type: application/json
Content-Length: 11

{"led":"0"}
```
!!! Note "JSON is Required"
    The only format accepted by the [`RESTServer`][urest.http.server.RESTServer] for the state of the nouns is [JSON](https://www.json.org/json-en.html). The [`RESTServer`][urest.http.server.RESTServer] will also only accept a sub-set of the JSON standard: notably assuming a single object, and a collection of key/value pairs.

![Figure 2: A Sequence Diagram for the Noun Set Request](../media/sd_http_set.svg)

**Figure 2: A Sequence Diagram for the Noun Set Request of the Example**

As before, the initial network request from the client is handled by the event
loop of the `asyncio` library, which will create instances of
[`asyncio.StreamReader`](https://docs.python.org/3.4/library/asyncio-stream.html#streamreader)
and
[`asyncio.StreamWriter`](https://docs.python.org/3.4/library/asyncio-stream.html#streamwriter)
to represent data being read from, or written to, the network respectively. Once
this is done, the `asyncio` library will call
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] to
handle the request.

The [`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun],
in turn, creates an instances of the [`HTTPResponse`]
[urest.http.response.HTTPResponse] class. This instance of [`HTTPResponse`]
[urest.http.response.HTTPResponse] is then set-up from the data read from the
HTTP headers via the
[`asyncio.StreamReader`](https://docs.python.org/3.4/library/asyncio-stream.html#streamreader).
Since this is a `PUT` request, the
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] will
also read the HTTP body from the client, parse into a JSON structure, and then use
this to set the desired `<< resource_state >>` to pass onto the noun handling the
request.

With the inital set-up complete,
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] calls
the relevant handler for the request. In this example [`SimpleLED.set_state()`]
[urest.examples.simpleled.SimpleLED] from an instance of
[`SimpleLED`][urest.examples.simpleled.SimpleLED] set-up earlier.

The exact interpretation of the JSON `<< resource_state >>` from the `Client` in
Figure 2 is left to the implementation of the noun. The only internal guarantee
provided by the library is the JSON will be parsed as far as possible and sent to
[`SimpleLED.set_state()`] [urest.examples.simpleled.SimpleLED], in this case, as a
Python `dict[str, Union[str, int]]`. For instance in the above example the key
`led` is interpreted as referring to the noun, and the value `0` as the state
value. In this case setting the GPIO `Pin 28` to the value `0` (or `off`). A close
correspondence between the name of the noun as referred to the API, and the name
of the noun in the state list is **strongly** advised: but is not strictly
required.

Once the [`SimpleLED.set_state()`][urest.examples.simpleled.SimpleLED] method
completes,
[`RESTServer.dispatch_noun()`][urest.http.server.RESTServer.dispatch_noun] passes
contol onto [`HTTPResponse`][urest.http.response.HTTPResponse] via the
[`HTTPResponse.send()`][urest.http.response.HTTPResponse.send]. The
[`HTTPResponse.send()`][urest.http.response.HTTPResponse.send] passes any
additional headers to the client via the [`asyncio.StreamWriter`](https://
docs.python.org/3.4/library/asyncio-stream.html#streamwriter): but otherwise
completes with the HTTP  response `200 OK`.

### Tested Implementations

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W
"""

### Expose the `http` module interface
from .response import HTTPResponse
from .server import RESTServer
