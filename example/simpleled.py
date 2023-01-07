# Import the Asynchronous IO Library, preferring the MicroPython library if
# available
try:
    from machine import Pin
except ImportError:
    print("Ignoring MicroPython include: machine")

from ..api.base import APIBase


class SimpleLED(APIBase):
    def __init__(self, pin):
        self._gpio = Pin(pin, Pin.OUT)
        self._gpio.off()

        self._state_attributes = dict(gpio=0)

    def set_state(self, state_attributes, selector=[]):
        try:
            _state_attributes["gpio"] = state_attributes["gpio"]

            if _state_attributes["gpio"]:
                self._gpio.off()
            else:
                self._gpio.on()

        except:
            # On exception try to return to a known good
            # state
            self._gpio.off()
            self._state_attributes["gpio"] = 0

    def get_state(self, selector=[]):
        return self._gpio.value()
