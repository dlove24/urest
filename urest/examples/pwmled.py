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
"""An example of a 'noun' class, able to serve as the basis for PWM control of
an LED attached to a suitable GPIO pin.

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

* Raspberry Pi Pico W
"""

# Import the Asynchronous IO Library, preferring the MicroPython library if
# available
try:
    import uasyncio as asyncio
    from machine import PWM, Pin
except ImportError:
    print("Ignoring MicroPython include: machine")

# Import the typing support
try:
    from typing import Union
except ImportError:
    from urest.typing import Union  # type: ignore


from urest.api.base import APIBase

PWM_STEP = 6550
"""Determines the increment (or decrement) for each step in the PWM 'on' or
'off' movement."""
PWM_LIMIT = 65000
"""Determines the limit for the PWM duty cycle."""


class PWMLED(APIBase):
    """Controls an LED by PWM modulation, and gives a reasonably minimal
    example of a 'noun' class, which inherits from `urest.api.base.APIBase`. It
    also requires the `Pin` library from MicroPython: but should be able to be
    adapted to other GPIO libraries which provide a similar interface.

    In contrast to the `urest.examples.simpleled.SimpleLED` class, the
    `urest.examples.pwmled.PWMLED` class shows the use of the `ayncio`
    `create_tasks()` hook within a `urest.api.base.APIBase` 'noun' to set off slow
    running tasks. This allows the state update to be returned to the network
    client via the API 'immediately' (at least subject to the other tasks
    outstanding and network conditions); without waiting for the _actual_ internal
    state to complete. This is a much more realistic scenario for use in the
    control of external devices: especially devices such as motors which may take
    seconds (or longer) to obtain the correct state.

    API
    ---

    The 'noun' exposes the following internal state, with allowed values as `0`
    or `1` for both keys.

    | JSON Key  | JSON Type | Description                                                             |
    |-----------|-----------|-------------------------------------------------------------------------|
    | `actual`  | `Integer` | The _current_ state of the controlled output                            |
    | `desired` | `Integer` | The _next_ state, if any, that the output is currently transitioning to |

    Since the class will not immediately set the `desired` state, but only once
    the full transition is complete, the client may not see any immediate changes
    in the `get_state` requests. Instead the full state table for the response,
    and interpretation, is as follows

    | Actual State | Desired State | Description                                                  |
    |--------------|---------------|--------------------------------------------------------------|
    | 0            | 0             | Output fully `off`                                           |
    | 0            | 1             | Output commanded `on`; currently turning from `off` to `on`  |
    | 1            | 0             | Output commanded `off`; currently turning from `on` to `off` |
    | 1            | 1             | Output fully `on`                                            |
    """

    def __init__(self, pin: int) -> None:
        self._gpio = PWM(Pin(pin))
        self._gpio.duty_u16(0)
        self._gpio.freq(100)
        self._gpio_lock = asyncio.Lock()

        self._duty = 0

        self._state_attributes = {"desired": 0, "current": 0}

    async def _slow_on(self) -> None:
        # Wait for the GPIO lock if we need to
        await self._gpio_lock.acquire()

        # Increase the duty cycle from 0 to near the
        # maximum in steps lasting 1s. We will also
        # allow other co-routines to run whilst we
        # are waiting for the next step to take place

        self._duty = 0

        while self._duty < (PWM_LIMIT):
            print(f"duty on: {self._duty}")

            self._duty += PWM_STEP
            self._gpio.duty_u16(self._duty)

            await asyncio.sleep_ms(1000)

        self._state_attributes["current"] = 1

        # Set the duty cycle to maximum before we leave,
        # and release the GPIO lock
        self._duty = 2**16
        self._gpio.duty_u16(self._duty)

        self._gpio_lock.release()

    async def _slow_off(self) -> None:
        # Wait for the GPIO lock if we need to
        await self._gpio_lock.acquire()

        # Decrease the duty cycle from the maximum to
        # near 0 in steps lasting 1s. We will also
        # allow other co-routines to run whilst we
        # are waiting for the next step to take place

        self._duty = 2**16

        while self._duty > PWM_STEP:
            print(f"duty off: {self._duty}")

            self._duty -= PWM_STEP
            self._gpio.duty_u16(self._duty)

            await asyncio.sleep_ms(1000)

        self._state_attributes["current"] = 0

        # Set the duty cycle to 0 before we leave,
        # and release the GPIO lock
        self._duty = 0
        self._gpio.duty_u16(self._duty)

        self._gpio_lock.release()

    def set_state(self, state_attributes: dict[str, Union[str, int]]) -> None:
        try:
            loop = asyncio.get_event_loop()

            self._state_attributes["desired"] = state_attributes["desired"]

            if self._state_attributes["desired"] == 0:
                self._state_attributes["current"] = 1

                loop.create_task(self._slow_off())
            else:
                self._state_attributes["current"] = 0

                loop.create_task(self._slow_on())

        except KeyError:
            # On exception try to return to a known good
            # state
            self._gpio.duty_u16(0)
            self._duty = 0

            self._state_attributes["desired"] = 0
            self._state_attributes["current"] = 0

    def get_state(self) -> dict[str, Union[str, int]]:
        return self._state_attributes

    def delete_state(self) -> None:
        self._gpio.duty_u16(0)
        self._gpio.freq(100)
        self._duty = 0

        self._state_attributes["desired"] = 0
        self._state_attributes["current"] = 0

    def update_state(
        self,
        state_attributes: dict[str, Union[str, int]],
    ) -> None:
        loop = asyncio.get_event_loop()

        if self._state_attributes["desired"] == 0:
            self._state_attributes["desired"] = 1
            self._state_attributes["current"] = 0

            loop.create_task(self._slow_on())
        else:
            self._state_attributes["desired"] = 0
            self._state_attributes["current"] = 1

            loop.create_task(self._slow_off())
