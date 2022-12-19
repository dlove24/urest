# Micro HTTP server dedicated to REST-style API Requests. Inspired by the
# '[MicroPython HTTP Server](https://github.com/erikdelange/MicroPython-HTTP-Server)'
# by Erik de Lange, as a simple consumer of the Python 3 `asyncio` library for the
# low-level socket handling and use of co-routines to simplify request handling.
#
# This version is written for MicroPython 3.4, and has been tested on:
#   * Raspberry Pi Pico W
#
# Copyright 2021 (c) Erik de Lange
# Copyright 2022 (c) David Love
# Released under MIT license

# Import the standard error library
import errno

# Import the Asynchronous IO Library
import uasyncio as asyncio

# Import the RAWResponse class
from .response import HTTPResponse


class RESTServerError(Exception):
    pass


class RESTServer:

    # Initialise the server with reasonable defaults. These should work
    # for most cases, and should be set so that most clients won't have
    # to touch them
    def __init__(
        self, host="0.0.0.0", port=80, backlog=5, read_timeout=30, write_timeout=5
    ):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self._server = None

    # Core client handling routine. This connects the `reader` and `writer`
    # streams from the IO library to the API requests detailed by the rest
    # of the server. Most of the work is done elsewhere, by the API handlers:
    # this is mostly a sanity check and a routing engine.
    #
    # **NOTE:** This routine _must_ handle arbitrary network traffic, and so
    #           **must** be as defensive as possible to avoid security issues in
    #           the API layer which results from arbitrary input stuffing and
    #           alike. Assume that anything in here is potentially dangerous to
    #           the health of the API layer: unless shown otherwise...
    async def _dispatch_noun(self, reader, writer):

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
                response.body = "<http><body><p>OK Request</p></body></http>"

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
            # for `timeout` seconds and then force the close
            await asyncio.sleep(self.write_timeout)
            await writer.wait_closed()

    async def start(self):
        print(f"SERVER: Started on {self.host}:{self.port}")
        self._server = await asyncio.start_server(
            self._dispatch_noun, self.host, self.port, self.backlog
        )

    async def stop(self):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            print("SERVER: Stopped")
        else:
            print("SERVER: Not started")
