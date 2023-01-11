"""
Micro HTTP server dedicated to REST-style API Requests. Inspired by the
[MicroPython HTTP Server](https://github.com/erikdelange/MicroPython-HTTP-Server)
by Erik de Lange, as a simple consumer of the Python 3 `asyncio` library for the
low-level socket handling and use of co-routines to simplify request handling.

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W


Standards
---------

  * For the HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt
  * For the JSON specification see: https://www.ecma-international.org/publications-and-standards/standards/ecma-404

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

# Import the API Base class
from ..api.base import APIBase

##
## Constants
##

ASCII_UPPERCASE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
""" Constant for the set of ASCII letters """
ASCII_DIGITS = set("0123456789")
""" Constant for the set of ASCII digits """
ASCII_EXTRA = set("_")
""" Constant for the extra ASCII characters allowed in the URI """

JSON_TYPE_INT = 0
""" Constant for JSON token type of Integer """
JSON_TYPE_STR = 1
""" Constant for JSON token type of String """
JSON_TYPE_ERROR = 1
""" Constant for JSON token type of error/unknown """

##
## Exceptions
##


class RESTServerError(Exception):
    pass


class RESTParseError(Exception):
    pass


##
## Classes
##


class RESTServer:

    #
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 80,
        backlog: int = 5,
        read_timeout: int = 30,
        write_timeout: int = 5,
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

        .. Note::
          The code in this class assumes the `asyncio` library with an interface
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

        port: integer
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
        self._nouns = {}

    def parse_data(self, data_str: str) -> dict:
        """
        Attempt to parse a string containing JSON-like formatting into a single dictionary.

        This function is **very** far from a full JSON parser: quite deliberately it will
        only accept a single object of name/value pairs. Any arrays are **not** accepted.
        In addition, this parser will coerce the 'name' side of the dictionary into a
        string; or if this cannot be done will raise a 'RESTParseError'. The 'value' of a
        name/value pair will like-wise be coerced into its JSON type; or a 'RESTParseError'
        raised if this cannot be done.

        The parsing is done via a very simple stack-based parser, assuming no backtracking.
        This will cope with valid JSON: but will quickly abort if the JSON is malformed,
        raising a 'RESTParseError'. This is quite deliberate as we will only accept valid
        JSON from the client: if we can't parse the result that is the clients problem...

        The parser will also finish after the first found JSON object. We are expecting
        only a single dictionary from the client, and so attempts to add something more
        exotic will be ignored.

        Parameters
        ----------

        data_str: str
            A JSON object string, representing a single dictionary

        Returns
        -------

        dict
          A mapping of (key, value) pairs which defines the dictionary of the `data_str`
          object. All `key` values will be in Python string format: values will be as
          defined in the `data_str` object.
        """

        return_dictionary = {}
        parse_stack = []
        object_start = False

        token_start = False
        token_sep = False

        token_type = JSON_TYPE_INT
        token_str = ""

        for char in data_str.decode("ascii"):

            # Look for the first object
            if char in ["{"]:
                object_start = True

            # If we are inside an object, attempt to assemble the
            # tokens
            if object_start:

                # If a '"' is found...
                if char in ['"']:

                    # ... and if we are building a token, this should be the
                    # end of a string, so push it to the stack ...
                    if token_start:
                        if token_type == JSON_TYPE_STR:
                            parse_stack.append(token_str)

                            token_start = False
                        else:
                            raise RESTParseError("Invalid string termination")

                        token_type = JSON_TYPE_INT
                        token_sep = False
                        token_start = False
                        token_str = ""

                    # ... Otherwise if we are not building a token, set the
                    # type marker, and start building a new string
                    else:
                        token_type = JSON_TYPE_STR
                        token_start = True
                        token_str = ""

                # Look for the separator between a 'key' and a 'value'
                if char in [":"]:
                    token_sep = True

                # Look for the end of a token
                if char in [",", "}"]:

                    # Add the key/value to the return dictionary if
                    # it appears to be valid
                    if token_sep:

                        if token_type == JSON_TYPE_INT:
                            # The token won't have been terminated
                            # so still should be in `token_str`
                            #
                            # NOTE: Technically an unterminated String
                            #       is an error, so will parsing will
                            #       break here (and we won't care)
                            parse_stack.append(token_str)

                        value = parse_stack.pop()
                        key = parse_stack.pop()

                        if token_type == JSON_TYPE_STR:
                            return_dictionary[key] = str(value)

                        if token_type == JSON_TYPE_INT:
                            return_dictionary[key] = int(value)

                    # If this is the end of the object, then return ...
                    if char in ["}"]:
                        return return_dictionary

                    # .. otherwise, cleanup and continue
                    else:
                        token_type = JSON_TYPE_ERROR
                        token_sep = False
                        token_start = False

                # If this isn't anything interesting, assume it is part of a token
                if object_start and (
                    (char in ASCII_UPPERCASE) or (char in ASCII_DIGITS)
                ):
                    token_str = token_str + char

        return return_dictionary

    def register_noun(self, noun: str, handler: APIBase):
        """
        Register a new object handler for the noun passed by the client.

        Parameters
        ----------

        noun: string
            String representing the noun to use in the API

        handler: `urest.api.base.APIBase`
            Object handling the request from the client
        """

        old_handler = None
        print("Register!")

        try:

            if noun in self._nouns:
                old_handler = self._nouns[noun]

            if isinstance(noun, str) and isinstance(handler, APIBase):
                self._nouns[noun.lower()] = handler

        except:
            if old_handler is not None:
                self._nouns[noun] = old_handler

    async def dispatch_noun(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        Core client handling routine. This connects the `reader` and `writer`
        streams from the IO library to the API requests detailed by the rest
        of the server. Most of the work is done elsewhere, by the API handlers:
        this is mostly a sanity check and a routing engine.

        .. Warning::
          This routine _must_ handle arbitrary network traffic, and so
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
            request_uri = await asyncio.wait_for(reader.readline(), self.read_timeout)
            request_uri = request_uri.decode("utf8")

            # Check for empty requests, and if found terminate the connection
            if request_uri in [b"", b"\r\n"]:
                # DEBUG
                print(
                    f"CLIENT: [{writer.get_extra_info('peername')[0]}] Empty request line"
                )
                return

            # DEBUG
            print(
                f"CLIENT URI : [{writer.get_extra_info('peername')[0]}] {request_uri}"
            )

            # Get the header of the request, if it is available, decoded into UTF-8
            request_header = {}
            request_line = None

            while not request_line in [b"", b"\r\n"]:
                request_line = await asyncio.wait_for(
                    reader.readline(), self.read_timeout
                )

                if request_line.find(b":") != -1:
                    name, value = request_line.split(b":", 1)
                    request_header[name.decode("utf-8").lower()] = value.decode(
                        "utf-8"
                    ).strip()

            # DEBUG
            print(
                f"CLIENT HEAD: [{writer.get_extra_info('peername')[0]}] {request_header}"
            )

            # Check if there is a body to follow the header ...
            request_body = {}

            if "content-length" in request_header:
                request_length = int(request_header["content-length"])
                print(f"content_length: {request_length}")

                # ... check if there is _really a body to follow ...
                if request_length > 0:

                    # ... if so, get the rest of the body of the request, decoded into UTF-8

                    try:
                        request_length = int(request_header["content-length"])
                        request_data = await asyncio.wait_for(
                            reader.read(request_length), self.read_timeout
                        )
                        print(request_data)
                        request_body = self.parse_data(request_data)
                    except Exception as e:
                        print(e)
                        request_body = {}

                # DEBUG
                print(
                    f"CLIENT BODY: [{writer.get_extra_info('peername')[0]}] {request_body}"
                )

            else:
                # DEBUG
                print("CLIENT BODY: NONE")

            ## NOTE: Below is a somewhat long-winded approach to working out
            ##       the verb is based on the longest assumed verb:
            ##       '`DELETE`'. To avoid later parsing errors, and to
            ##       filter out the rubbish which might cause security
            ##       issues, we will search first for a 'space' within
            ##       the first six characters; then take either the first
            ##       six characters or the string up to the 'space'
            ##       whichever is shorter. These can then be compared
            ##       for sanity before we run the dispatcher

            # Work out the action we need to take ...

            first_space = request_uri.find(" ", 0, 7)

            if first_space > 7:
                first_space = 7

            verb = request_uri[0:first_space].upper()

            # ... Work out the noun defining the class we need to use to resolve the
            # action ...

            uri_root = request_uri.find("/", first_space)

            noun = ""
            start_noun = False

            for char in request_uri[uri_root:]:
                if (
                    (char in ASCII_UPPERCASE)
                    or (char in ASCII_DIGITS)
                    or (char in ASCII_EXTRA)
                ):
                    start_noun = True
                    noun = noun + char
                else:
                    if start_noun:
                        break

            # ... and then call the appropriate handler
            response = HTTPResponse()

            if verb == "DELETE":
                self._nouns[noun.lower()].delete_state()
                response.body = ""

            elif verb == "GET":
                return_state = self._nouns[noun.lower()].get_state()
                response_str = "{"

                try:
                    for key in return_state:
                        if isinstance(return_state[key], int):
                            response_str = (
                                response_str + f'"{key.lower()}": {return_state[key]},'
                            )
                        else:
                            response_str = (
                                response_str
                                + f'"{key.lower()}": "{return_state[key]}",'
                            )
                finally:
                    # Properly terminate the body
                    response_str = response_str[:-1] + "}"

                response.body = response_str

            elif verb == "POST":
                self._nouns[noun.lower()].set_state(request_body)
                response.body = ""

            elif verb == "PUT":
                self._nouns[noun.lower()].set_state(request_body)
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

            print(f"!EXCEPTION!: {e}")

            response.body = "<http><body><p>Invalid Request</p></body></http>"
            response.status = "NOT_OK"

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
