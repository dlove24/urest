"""
Micro HTTP server dedicated to REST-style API Requests. Inspired by the
[MicroPython HTTP Server](https://github.com/erikdelange/MicroPython-HTTP-Server)
by Erik de Lange, as a simple consumer of the Python 3 `asyncio` library for the
low-level socket handling and use of co-routines to simplify request handling.

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W


Standards
---------

  * For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt

Licence
-------

This module, and all included code, is made available under the terms of the MIT
Licence

> Copyright 2022 (c) Erik de Lange, Copyright (c) 2022-2023 David Love

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

# Import the standard error library
import errno

# Import the Asynchronous IO Library, preferring the MicroPython library if
# available
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

# Import the RAWResponse class
from .response import HTTPResponse


class RESTServerError(Exception):
    pass


class RESTServer:

    #
    def __init__(
        self, host="0.0.0.0", port=80, backlog=5, read_timeout=30, write_timeout=5
    ):
        """Initialise the server with reasonable defaults. These should work
        for most cases, and should be set so that most clients won't have
        to touch them.

        The `urest.http.server.RESTServer` class acts as the primary interface
        to the library, handling all the network communication with the client,
        formatting the response and marshalling the API calls required to generate that
        response.

        In most cases consumers of this module will create a single instance of
        the `urest.http.server.RESTServer` class, and then pass the reference to the
        `urest.http.server.RESTServer.start` method to an event loop of the `asyncio`
        library.

        For example the following code creates a variable `app` for the instance
        of the `urest.http.server.RESTServer` class, and passes this to the 'main' event
        loop of the `asyncio` library

        ```python
        app = RESTServer()


        if __name__ == "__main__":
          loop = asyncio.get_event_loop()
          loop.create_task(app.start())
          loop.run_forever()
        ```

        The `urest.http.server.RESTServer.start` method is expected to be used
        in a [`asyncio` event
        loop](https://docs.python.org/3.4/library/asyncio-eventloop.html), as above;
        with the tasks being handled by the `urest.http.server.RESTServer.dispatch_noun`
        method. If the event loop is required to be closed, or destroyed, the tasks
        can be removed using the `urest.http.server.RESTServer.stop` method.

        **NOTE:** The code in this class assumes the `asyncio` library with an interface
        roughly equivalent to Python 3.4: although the MicroPython module supports _some_
        later extensions. Given the code churn in the `asyncio` module between Python 3.4
        and Python 3.10, careful testing is required to ensure implementation compatibility.

        Parameters
        ----------

        host: string
            A resolvable DNS host name or IP address. Note that the exact requirements are
            determined by the
            [`asyncio.BaseEventLoop.create_server`](https://docs.python.org/3.4/library/
            asyncio-eventloop.html#asyncio.BaseEventLoop.create_server) method, which should
            be checked carefully for implementation defined limitations.

            **Default:** An IPv4 sock on the local host.

        port: string
            The local (server) port to bind the socket to. Note that the exact requirements are
            determined by the
            [`asyncio.BaseEventLoop.create_server`](https://docs.python.org/3.4/library/
            asyncio-eventloop.html#asyncio.BaseEventLoop.create_server) method, which should
            be checked carefully for implementation defined limitations (e.g. extra privileges
            required for system ports).

            **Default:** The IANA Assigned port 80 for an HTTP Server.

        backlog: integer
            Roughly the size of the pool of connections for the underlying
            `socket`. Once this value has been exceeded, the tasks will be suspended by the
            co-routine handler until the underlying `socket` can clear them. Note that the
            size (and interpretation) of this value is system dependent: see the [`socket`
            API](https://docs.python.org/3.4/library/socket.html#module-socket) for more
            details.

            **Default:** 5 (typically the maximum pool size allowed).

        read_timeout: integer
            Length of time in seconds to wait for a response from the client before declaring
            failure.

            **Default:** 30 seconds.

        write_timeout: integer
            Length of time in seconds to wait for the network socket to accept a write to the
            client, before declaring failure.

            **Default:** 5 seconds.

        """

        self.host = host
        self.port = port
        self.backlog = backlog
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self._server = None

    async def dispatch_noun(self, reader, writer):
        """
        Core client handling routine. This connects the `reader` and `writer`
        streams from the IO library to the API requests detailed by the rest
        of the server. Most of the work is done elsewhere, by the API handlers:
        this is mostly a sanity check and a routing engine.

        **NOTE:** This routine _must_ handle arbitrary network traffic, and so
                **must** be as defensive as possible to avoid security issues in
                the API layer which results from arbitrary input stuffing and
                alike. Assume that anything from the `reader` is potentially
                dangerous to the health of the API layer: unless shown otherwise...



        Parameters
        ----------

        reader: `asyncio.StreamReader`
            An asynchronous stream, representing the network response _from_ the
            client. This is usually set-up indirectly by the `asyncio` library as part of a
            network response to the client, and will be represented by an
            [asyncio.StreamReader](https://docs.python.org/3.4/library/asyncio-stream.html#
            streamreader).

        writer: `asyncio.StreamWriter`
            An asynchronous stream, representing the network response _to_ the
            client. This is usually set-up indirectly by the `asyncio` library as part of a
            network response to the client, and will be represented by an
            [asyncio.StreamWriter](https://docs.python.org/3.4/library/asyncio-stream.html#
            streamwriter).
        """

        # Attempt the parse whatever rubbish the client sends, and assemble the
        # fragments into an API request. Any failures should result in an
        # `Exception`: success should result in an API call
        try:

            # Get the raw network request and decode into UTF-8
            request_line = await asyncio.wait_for(reader.readline(), self.read_timeout)
            request_line = request_line.decode("utf8")

            # Check for empty requests, and if found terminate the connection
            if request_line in [b"", b"\r\n"]:
                print(
                    f"CLIENT: [{writer.get_extra_info('peername')[0]}] Empty request line"
                )
                return

            # DEBUG
            print(f"CLIENT: [{writer.get_extra_info('peername')[0]}] {request_line}")

            # Work out the action we need to take ...
            # NOTE: This somewhat long-winded approach to working out
            #       the verb is based on the longest assumed verb:
            #       '`DELETE`'. To avoid later parsing errors, and to
            #       filter out the rubbish which might cause security
            #       issues, we will search first for a 'space' within
            #       the first six characters; then take either the first
            #       six characters or the string up to the 'space'
            #       whichever is shorter. These can then be compared
            #       for sanity before we run the dispatcher
            first_space = request_line.find(" ", 0, 6)

            if first_space > 6:
                first_space = 6

            verb = request_line[0:first_space].upper()

            # ... and then call the appropriate handler
            response = HTTPResponse()

            if verb == "DELETE":
                response.body = ""

            elif verb == "GET":
                response.body = "<http><body><p>Test Request</p></body></http>"

            elif verb == "POST":
                response.body = ""

            elif verb == "PUT":
                response.body = ""

            else:
                # Clearly not one of ours
                response.body = "<http><body><p>Invalid Request</p></body></http>"
                response.status = "NOT_OK"

            await response.send(writer)

            writer.write("\n")

            await writer.drain()

        # Deal with any exceptions. These are mostly client errors, and since the REST
        # API _should_ be idempotent, the client _should_ be able to simply retry. So
        # we won't do anything very fancy here
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            if e.args[0] == errno.ECONNRESET:  # connection reset by client
                pass
            else:
                raise e

        # In principle the response should have been sent back to the client by now.
        # But we will give it one last try, and then also try to close the connection
        # cleanly for the client. This may not work due to the earlier exceptions: but
        # we will try anyway
        finally:
            # Do a soft close, dropping our end of the connection
            # to see if the client closes ...
            await writer.drain()
            writer.close()

            # ... if the client doesn't take the hint, wait
            # for `write_timeout` seconds and then force the close
            await asyncio.sleep(self.write_timeout)
            await writer.wait_closed()

    async def start(self):
        """
        Attach the method `urest.http.server.RESTServer.dispatch_noun` to an `asyncio`
        event loop, allowing the `urest.http.server.RESTServer.dispatch_noun` method to
        handle tasks representing network events from the client.

        Most of the implementation of this method is handled by
        [asyncio.start_server](https://docs.python.org/3.4/library/asyncio-stream.html#
        asyncio.start_server). In particular the
        [asyncio.start_server](https://docs.python.org/3.4/library/asyncio-stream.html#
        asyncio.start_server) method is responsible for setting up the lower-level
        networks socket, using the `host` and `port` class attributes holding the server
        (local) elements of the TCP/IP tuple. Lower level timers and queues are also
        provided by the resolution of the
        [asyncio.start_server](https://docs.python.org/3.4/library/asyncio-stream.html#
        asyncio.start_server) method, with the class attribute `backlog` being used to
        set the client (downstream) timeout.
        """

        print(f"SERVER: Started on {self.host}:{self.port}")
        self._server = await asyncio.start_server(
            self.dispatch_noun, self.host, self.port, self.backlog
        )

    async def stop(self):
        """
        Remove the tasks from an event loop, in preparation for the termination
        of that loop. Most of the implementation of this method is handled by the
        [`close`
        method](https://docs.python.org/3.4/library/asyncio-protocol.html#asyncio.
        BaseTransport.close) of `asyncio.BaseTransport`.
        """

        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            print("SERVER: Stopped")
        else:
            print("SERVER: Not started")
