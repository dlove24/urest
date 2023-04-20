# This class, and all included code, is made available under the terms of the MIT Licence
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

"""
An example of a 'noun' class, able to serve as the basis for control of an LED attached to a GPIO pin.

Overview
--------

This is a reasonably minimal example of a 'noun' class, which inherits from
`urest.api.base.APIBase`. It also requires the `Pin` library from MicroPython:
but should be able to be adapted to other GPIO libraries which provide a similar
interface.

For an example of an application which uses this library, see: `urest.examples.led_control`

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W

"""


# Import the Asynchronous IO Library, preferring the MicroPython library if
# available
try:
    from machine import Pin
except ImportError:
    print("Ignoring MicroPython include: machine")

from urest.api.base import APIBase


class SimpleLED(APIBase):
    def __init__(self, pin: Pin) -> None:
        self._gpio = Pin(pin, Pin.OUT)
        self._gpio.off()

        self._state_attributes = {"led": 0}

    def set_state(self, state_attributes: dict) -> None:
        try:
            self._state_attributes["led"] = state_attributes["led"]

            if self._state_attributes["led"] == 0:
                self._gpio.off()
            else:
                self._gpio.on()

        except KeyError:
            # On exception try to return to a known good
            # state
            self._gpio.off()
            self._state_attributes["led"] = 0

    def get_state(self) -> dict:
        return {"led": self._gpio.value()}

    def delete_state(self) -> None:
        self._gpio.off()
        self._state_attributes["led"] = 0

    def update_state(self, state_attributes: dict) -> None:
        if self._state_attributes["led"] == 0:
            self._gpio.on()
            self._state_attributes["led"] = 1
        else:
            self._gpio.off()
            self._state_attributes["led"] = 0
