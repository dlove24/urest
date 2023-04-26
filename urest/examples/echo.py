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
"""An example of a 'noun' class which echo's responses to the client. The main
use of this library is as a test: it should work on both the Pico (W) boards
and any 'normal' installation of Python. As such it provides very little
functionality, but could in principle also be used as a the basis for a more
useful test harness or stub.

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W
"""


# Import the typing support
try:
    from typing import Union
except ImportError:
    from urest.typing import Union  # type: ignore


from urest.api.base import APIBase


class EchoServer(APIBase):
    """An example of a 'noun' class which echo's responses to the client. The
    main use of this library is as a test: it should work on both the Pico (W)
    boards and any 'normal' installation of Python. As such it provides very
    little functionality, but could in principle also be used as a the basis
    for a more useful test harness or stub.

    For an example of the client part of the 'echo server', see the example
    [`echo_server.py`](https://github.com/dlove24/urest/blob/trunk/examples/echo_server.py).
    A full example of this class is also described in the
    [_Simple Echo Server_][a-simple-echo-server-windows-linux-and-mac] How-To.

    API
    ---

    The 'noun' exposes the following internal state

    | JSON Key | JSON Type | Description                                                       |
    |----------|-----------|-------------------------------------------------------------------|
    | `echo`   | `Integer` | Holds the current state of the resource, determined by the client |

    This state can be altered by the client sending either a `0` or `1` to the
    `noun`: which will record the last value seen from the client. This last
    value can then be returned to the client on request. Values greater than `1`
    will be treated as `1` for the purposes of setting the state.
    """

    def __init__(self) -> None:
        self._state = False
        self._state_attributes = {"echo": 0}

    def set_state(self, state_attributes: dict[str, Union[str, int]]) -> None:
        try:
            self._state_attributes["echo"] = state_attributes["echo"]

            if self._state_attributes["echo"] == 0:
                self._state = False
            else:
                self._state = True

        except KeyError:
            # On exception try to return to a known good
            # state
            self._state = False
            self._state_attributes["echo"] = 0

    def get_state(self) -> dict[str, Union[str, int]]:
        return {"echo": self._state}

    def delete_state(self) -> None:
        self._state = False
        self._state_attributes["echo"] = 0

    def update_state(
        self,
        state_attributes: dict[str, Union[str, int]],
    ) -> None:
        if self._state_attributes["echo"] == 0:
            self._state = True
            self._state_attributes["echo"] = 1
        else:
            self._state = False
            self._state_attributes["echo"] = 0
