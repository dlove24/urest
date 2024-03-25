# This module, and all included code, is made available under the terms of the MIT Licence
#
# Copyright (c) 2022--2023 David Love
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
"""The core of the API being created for the network clients is provided
through the [`APIBase`][urest.api.base.APIBase] class. This reference describes
the core [`APIBase`][urest.api.base.APIBase] class, together with example
implementations (sub-classes) from the `urest.example` package.

The [`APIBase`][urest.api.base.APIBase] class delegates all network requests to
the [`RESTServer`][urest.http.server.RESTServer] class ([described separately]
[the-urest-server-implementation]). During the marshalling of client requests
by the [`RESTServer`][urest.http.server.RESTServer] class, the path
portion of the URI is extracted from the client. This path is expected to take the
form of

> `/< noun >`

with the 'verb' denoted by the HTTP methods. Each 'noun' is implemented by a class
which inherits from [`APIBase`][urest.api.base.APIBase]. The 'noun' determines the
resource of the request (i.e. derived class), and the 'verb' the action to be
taken on that resource. Also important is the intent of the client as inferred
from the underlying HTTP request, e.g. `GET` or `PUT`. Taken together the URI and
the client intent are mapped to methods of [`APIBase`][urest.api.base.APIBase] as
follows

| Verb   | HTTP Method | [`APIBase`][urest.api.base.APIBase] method      |
|--------|-------------|--------------------------------------------|
| Get    | `GET`       | [`APIBase.get_state()`][urest.api.base.APIBase.get_state]    |
| Set    | `PUT`       | [`APIBase.set_state()`][urest.api.base.APIBase.set_state]    |
| Update | `POST`      | [`APIBase.update_state()`][urest.api.base.APIBase.update_state] |
| Delete | `DELETE`    | [`APIBase.delete_state()`][urest.api.base.APIBase.delete_state] |

## Routing Requests

All nouns are registered with [`RESTServer`][urest.http.server.RESTServer] in **lowercase**. Likewise all routing of API requests will also assume that the name of the noun to be used will be in lowercase. Thus, for instance, calling

```python
app.register_noun('leD', SimpleLED(28))
```

or

```python
app.register_noun('LED', SimpleLED(28))
```

will **all** route to the name noun with the canonical name `led`. Likewise
the request

```
GET /lEd HTTP 1.1
```

or

```
GET /LED HTTP 1.1
```

will **also** route to the same noun with the canonical name `led`.

!!! Note
    All nouns are checked by [`RESTServer`][urest.http.server.RESTServer], and
    nouns will not be properly routed unless [`APIBase`][urest.api.base.APIBase]
    is an ancestor of the derived class. Thus, for example, the [`SimpleLED`]
    [urest.examples.simpleled.SimpleLED] class above **must** also be a sub-class
    of [`APIBase`][urest.api.base.APIBase] for [`RESTServer`]
    [urest.http.server.RESTServer] to route the request properly.

## Package and Class Structure

The [`APIBase`][urest.api.base.APIBase] class is an _abstract base class_ and provides minimal services beyond defining the core interface (or protocol) for [`RESTServer`][urest.http.server.RESTServer]. As outlined above, this interface is provided though the core class methods as shown below

![API Package Structure](../media/urest_api.svg)

The API services for the network clients are then expected to be built from the _abstract base class_ of [`APIBase`][urest.api.base.APIBase]. The `urest` library provides a number of examples in the `urest.examples` package, which illustrate some way of using the library. Many of these are also used by the code in the [`examples` folder](https://github.com/dlove24/urest/tree/trunk/examples) of the source repository. The classes of the `urest.examples` package are described later, but can be conceptually defined as follows

![API Package Structure](../media/urest_examples.svg)

## Example Usage

### Getting the Noun State

This example is based on the [`SimpleLED`][urest.examples.simpleled.SimpleLED]
class as a minimal implementation of a noun controlling a GPIO pin, using the
MicroPython `Pin` library. The full documentation for the class is detailed below,
and the [`SimpleLED`][urest.examples.simpleled.SimpleLED] is available through the
`urest.examples` package.

For the [`SimpleLED`][urest.examples.simpleled.SimpleLED] class, the exact pin
being controlled is set during the object instantiation, via the class
constructor. Assuming the [`RESTServer`][urest.http.server.RESTServer] has been
created as

```python
app = RESTServer()
```

then a 'noun' `led` can be registered via the [`RESTServer.register_noun()`][urest.http.server.RESTServer.register_noun] method as

```python
app.register_noun('led', SimpleLED(28))
```

This will also create an instance of the [`SimpleLED`]
[urest.examples.simpleled.SimpleLED] class, bound to the controlled GPIO
pin `Pin 28`. Documentation for the micro-controller and platform being used will
be need to determine suitable values for the GPIO pin numbering.

Once the 'noun' has been registered, then the state of GPIO `Pin 28` can be
found by the HTTP request

```
GET /led HTTP 1.1
```

On receiving the above request from the client, the [`RESTServer`][urest.http.server.RESTServer] instance will call the relevant methods of the [`SimpleLED`]
[urest.examples.simpleled.SimpleLED] (as a sub-class of [`APIBase`][urest.api.base.APIBase]) as shown in Figure 1. Note that the '`<< resource state>>`' returned by [`SimpleLED.get_state()`]
[urest.examples.simpleled.SimpleLED] is as a Python `dict[str, Union[str, int]]`. The full return of data to the client, including relevant HTTP headers, conversion to JSON, etc. is handeled by the [`RESTServer`][urest.http.server.RESTServer] instance.

![Figure 1: A Sequence Diagram for the Noun Get Request](../media/sd_api_get.svg)

**Figure 1: A Sequence Diagram for the Noun Get Request of the Example**

### Setting the Noun State

Setting the state of the noun is a little more involved, as this will require
the desired state of the noun to be sent to the server. A useful tool for
testing purposes is the [curl](https://curl.se) utility; available on most
platforms.

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

![Figure 2: A Sequence Diagram for the Noun Set Request](../media/sd_api_set.svg)

**Figure 2: A Sequence Diagram for the Noun Set Request of the Example**

The exact interpretation of the JSON `<< resource_state >>` from the `Client` in Figure 2 is left to the implementation of the noun. The only internal guarantee provided by the library is the JSON will be parsed as far as possible and sent to [`SimpleLED.set_state()`] [urest.examples.simpleled.SimpleLED], in this case, as a Python `dict[str, Union[str, int]]`. For instance in the above example the key `led` is interpreted as referring to the noun, and the value `0` as the state value. In this case setting the GPIO `Pin 28` to the value `0` (or `off`). A close correspondence between the name of the noun as referred to the API, and the name of the noun in the state list is **strongly** advised: but is not strictly required.

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W
"""

### Expose the `http` module interface
from .base import APIBase
