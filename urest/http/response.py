# This module, and all included code, is made available under the terms of the MIT
# Licence
#
# Copyright 2022 (c) Erik de Lange, Copyright (c) 2022-2023 David Love
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
Formats a basic HTTP/1.1 response. The actual body of the response is largely
determined by the callers API layer: `urest.http.response.HTTPResponse` is a
utility class designed just handles to handle the raw response to the network
client. As such it should be largely invisible to the API layer, and most
consumers of the `urest.http` module _should not_ create instance of the
`urest.http.response.HTTPResponse` class directly

Standards
---------

  * For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt
  * For MIME types see: https://www.iana.org/assignments/media-types/media-types.xhtml
"""

# Import the Asynchronous IO Library, preferring the MicroPython library if
# available
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

# Import the enumerations library.
# from enum import Enum
# Unfortunately not in MicroPython yet, so we can't enforce the type
HTTPStatus = {"OK", "NOT_OK", "NOT_FOUND"}
"""
    Define the HTTP response codes in use. See the Mozilla [HTTP response status
    codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) for more
    details
"""


class HTTPResponse:
    ##
    ## Constructor
    ##

    def __init__(
        self,
        body: str = "",
        status: HTTPStatus = "OK",
        mimetype: str = None,
        close: bool = True,
        header: dict = None,
    ):
        """Create a response object, representing the raw HTTP header returned to the
        network client.

        This instance is guaranteed to be a valid _class_ on creation, and
        _should_ also be a valid HTTP response. However the caller should check the
        validity of the header before returning to the client. In particular,  responses
        returned to the client by this class _must_ be formatted according to the
        [HTTP/1.1 specification](https://www.ietf.org/rfc/rfc2616.txt) and _must_ be
        valid.

        Parameters
        ----------

        body: string
            The raw HTTP body returned to the client. This is `Empty` by default as
            the return string is usually built by the caller via the `getters` and
            `setters` of `urest.http.response.HTTPResponse`
        status: urest.http.response.HTTPStatus
            HTTP status code, which must be formed from the set
            `urest.http.response.HTTPResponse`. Arbitrary return codes are **not**
            supported by this class.
        mimetype: string
            A valid HTTP mime type. This is `Empty` by default and should be set
            once the `body` of the `urest.http.response.HTTPResponse` has been
            created.
        close: bool
            When set `True` the connection to the client will be closed by the
            `urest.http.server.RESTServer` once the `urest.http.response.HTTPResponse`
            has been sent. Otherwise, when set to `False` this will flag to the
            client that the created `urest.http.response.HTTPResponse` is part of
            a sequence to be sent over the same connection.
        header:  Dictionary
            Raw (key, value) pairs for HTTP response header fields. This allows
            setting of arbitrary fields by the caller, without extending/sub-classing
            `urest.http.response.HTTPResponse`

        """

        if status in HTTPStatus:
            self._status = status
        else:
            raise ValueError(
                "Invalid HTTP status code passed to the HTTP Response class"
            )

        if body is not None and isinstance(body, str):
            self._body = body
        else:
            self._body = ""

        self._mimetype = mimetype
        self._close = close

        if header is None:
            self._header = {}
        else:
            self._header = header

    ##
    ## Getters and Setters
    ##

    # HTTP Body

    @property
    def body(self):
        """The raw HTTP response, formatted to return to the client as the HTTP response."""

        return self._body

    @body.setter
    def body(self, new_body: str):
        if new_body is not None and isinstance(new_body, str):
            self._body = new_body
        else:
            self._body = ""

    # HTTP Status

    @property
    def status(self):
        """
        A valid `urest.http.response.HTTPResponse` representing the current
        error/status code that will be returned to the client.
        """
        return self._status

    @status.setter
    def status(self, new_status: HTTPStatus):
        if new_status in HTTPStatus:
            self._status = new_status
        else:
            raise ValueError(
                "Invalid HTTP status code passed to the HTTP Response class"
            )

    ##
    ## Functions
    ##

    async def send(self, writer: asyncio.StreamWriter):
        """Send an appropriate response to the client, based on the status code.

        This method assembles the full HTTP 1.1 header, based on the `mimetype`
        the content currently in the `body`, and the error code forming the
        `status` of the response to the client.

        .. Note::
          The the actual sending of this HTTP 1.1 header to the client
          is the responsibility of the caller. This function only assists in correctly
          forming that response

        Parameters
        ----------

        writer: `asyncio.StreamWriter`
            An asynchronous stream, representing the network response to the
            client. This is usually set-up indirectly by the caller as part of a network
            response to the client. As such is is usually just a pass-though from the
            dispatch call of the server. For an example see the dispatcher
            `urest.http.server.RESTServer.dispatch_noun`.

        Returns
        -------

        `async`

            The return type is complex, and indicates this method is expected to be run
            as a co-routine under the `asyncio` library.
        """

        # **NOTE**: This implementation should be in "match/case", but MicroPython
        #       doesn't have a 3.10 release yet. When it does, this
        #       implementation should be updated

        if "OK" in self._status:
            # First tell the client we accepted the request
            writer.write("HTTP/1.1 200 OK\n".encode())

            # Then we try to assemble the body
            if self._mimetype is not None:
                writer.write(f"Content-Type: {self.mimetype}\n".encode())

        elif "NOT_OK" in self._status:
            # Tell the client we think we can route it: but the request
            # makes no sense
            writer.write("HTTP/1.1 400 Bad Request\n".encode())

        elif "NOT_FOUND" in self._status:
            # Tell the client we can't route their request
            writer.write("HTTP/1.1 404 Not Found\n".encode())

        else:
            # This _really_ shouldn't be here. Assume an internal error
            writer.write("HTTP/1.1 500 Internal Server Error\n".encode())

        # Send the body length
        writer.write(f"Content-Length: {len(self._body)}\n".encode())

        # Send the body content type
        writer.write("Content-Type: text/html\n".encode())

        # Send any other header fields
        if len(self._header) > 0:
            for key, value in self._header.items():
                writer.write(f"{key}: {value}\n".encode())

        # Send the HTTP connection state
        if self._close:
            writer.write("Connection: close\n".encode())
        else:
            writer.write("Connection: keep-alive\n".encode())

        # Send the body itself...
        writer.write(f"\n{self._body}\n".encode())

        # ... and ensure that it gets back to the client
        await writer.drain()
