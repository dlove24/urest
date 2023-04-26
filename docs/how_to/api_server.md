# Creating a Network Server

## Overview

All network clients are assumed to be handled by an instance of the [`RESTServer`]
[urest.http.server.RESTServer] class from the `urest.http.server` module. The
[`RESTServer`][urest.http.server.RESTServer] class provides both an event loop for
the `asyncio` library, and also takes care of the lower-level networking interface
for the clients. Unless working with multiple instances (e.g. via a thread
library), most model consumers are assumed have a single instance of the
[`RESTServer`][urest.http.server.RESTServer] -- **but the module will not check
this**.

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

!!! Warning
    There is no guarantee of thread-safety in this module, and all
    'concurrency' is assumed to be via co-routines provided by the `asyncio`
    library. For an overview of how multiple clients can be handled using
    co-routines, [Async IO in Python](https://realpython.com/async-io-python) is
    highly recommended reading.

### Creating the API Responses

Most module consumers will not use the [`urest.http.response`][urest.http.response]
module directly: but will instead sub-class [`APIBase`][urest.api.base.APIBase] to
provide the core of the response to the network clients. For details of how the
[`RESTServer`][urest.http.server.RESTServer] and [`APIBase`]
[urest.api.base.APIBase] classes interact, the module documentation for
`urest.api` should be consulted. In addition, the documentation for the
[`SimpleLED`][urest.examples.simpleled.SimpleLED] might prove useful as an example
of a simple implementation of the API.
