# Formats a basic HTTP/1.1 response. The actual body of the response is largely
# determined by the callers API layer: this just handles the raw response to the
# network client. As such it should be largely invisible to the API layer.
#
# For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt
# For MIME types see: https://www.iana.org/assignments/media-types/media-types.xhtml
#
# Copyright 2022 (c) Erik de Lange
# Copyright 2022 (c) David Love
# Released under MIT license

# Import the enumerations library. Unfortunately not in MicroPython yet
# from enum import Enum

# Define the HTTP response codes in use. See the Mozilla [HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) for more details
HTTPStatus = {"OK", "NOT_OK", "NOT_FOUND"}


class HTTPResponse:

    ##
    ## Constructor
    ##

    def __init__(self, body="", status="OK", mimetype=None, close=True, header=None):
        """Create a response object

        :param string _body: HTTP return body
        :param HTTPStatus _status: HTTP status code
        :param str _mimetype: HTTP mime type
        :param bool _close: if true close connection else keep alive
        :param dict _header: key,value pairs for HTTP response header fields
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
        return self._body

    @body.setter
    def body(self, new_body):
        if new_body is not None and isinstance(new_body, str):
            self._body = new_body
        else:
            self._body = ""

    # HTTP Status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if new_status in HTTPStatus:
            self._status = new_status
        else:
            raise ValueError(
                "Invalid HTTP status code passed to the HTTP Response class"
            )

    ##
    ## Functions
    ##

    async def send(self, writer):
        """Send response to stream writer"""

        # Send an appropriate response, based on the status code
        #
        # NOTE: This really should be in "match/case", but MicroPython
        #       doesn't have a 3.10 release yet. When it does, this should
        #       be updated
        if "OK" in self._status:
            # First tell the client we accepted the request
            writer.write(f"HTTP/1.1 200 OK\n")

            # Then we try to assemble the body
            if self._mimetype is not None:
                writer.write(f"Content-Type: {self.mimetype}\n")

        elif "NOT_OK" in self._status:
            # Tell the client we think we can route it: but the request
            # makes no sense
            writer.write(f"HTTP/1.1 400 Bad Request\n")

        elif "NOT_FOUND" in self._status:
            # Tell the client we can't route their request
            writer.write(f"HTTP/1.1 404 Not Found\n")

        else:
            # This _really_ shouldn't be here. Assume an internal error
            writer.write(f"HTTP/1.1 500 Internal Server Error\n")

        # Send the body length
        writer.write(f"Content-Length: {len(self._body)}\n")

        # Send the body content type
        writer.write(f"Content-Type: text/html\n")

        # Send any other header fields
        if len(self._header) > 0:
            for key, value in self._header.items():
                writer.write(f"{key}: {value}\n")

        # Send the HTTP connection state
        if self._close:
            writer.write("Connection: close\n")
        else:
            writer.write("Connection: keep-alive\n")

        # Send the body itself...
        writer.write(f"\n{self._body}\n")

        # ... and ensure that it gets back to the client
        await writer.drain()
