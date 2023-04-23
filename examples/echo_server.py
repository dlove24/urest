# This class, and all included code, is made available under the terms of the MIT Licence
#
# Copyright (c) 2023 David Love
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
"""The server used in the Tutorial "_A Simple Echo Server_". This provides a
minimal 'echo' server to test the client against, and make sure all of the set-
up steps are working.

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W
"""

import time

import urest.utils

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from urest.api import APIBase
from urest.examples.echo import EchoServer
from urest.http import RESTServer

###
### Connect to the Wireless network
###

urest.utils.wireless_enable("SSID", "PASSWORD")

###
### Main Loop
###

# Create the server ...
app = RESTServer(port=8024)

# ... and register the nouns
try:
    app.register_noun("echo", EchoServer())
except NameError:
    print("Cannot initalise the API")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
