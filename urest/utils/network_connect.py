# This module, and all included code, is made available under the terms of the MIT
# Licence
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

"""
Utility function and exceptions which handle the network initialisation for the Pico W. The majority of this library is boiler-plate, and mimics the C library set-up required by the Pico W. For compatibility with that library (and the documentation) the `Exception` names in this module mirror those of the C library.

!!! warning "Pico W Only"

    This function will _only_ work on the Pico W, and with the Pico W
    network library. Loading this function on a Pico H, or without the Pico W
    network library, will result in an error.

References
----------

* [Raspberry Pi Pico Python SDK](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf)
* [Connecting to the Internet with Raspberry Pi Pico W, Chapter 3, Section 3.6](https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf)
"""

# Import the Python type libraries if available
try:
    from typing import Union
except ImportError:
    print("The Python type library isn't present. Ignoring.")

try:
    import time

    from machine import Pin
    from micropython import const
except ImportError:
    print("Ignoring MicroPython includes")

try:
    import network
except ImportError:
    print("Warning: Cannot find the network library. Ignoring")

##
## Attributes. Taken from the Pico W C library headers
##

CYW43_LINK_DOWN = const(0)
"""Failure code indicating the wireless link is unavailable. Check the SSID is correct."""
CYW43_LINK_JOIN = const(1)
"""Failure code indicating the SSID or password is incorrect and the specified SSID cannot be joined. Check the SSID and password."""
CYW43_LINK_NOIP = const(2)
"""Failure code indicating the join request was successful: but no IP address was returned. Check the DHCP settings for the specified SSID"""
CYW43_LINK_UP = const(3)
"""Success code indicating a successful join, and that an IP address was obtained from the network"""
CYW43_LINK_FAIL = const(-1)
"""General failure code. The link specified by the SSID is unavailable for unknown reasons."""
CYW43_LINK_NONET = const(-2)
"""General failure code _after_ authentication. The authentication likely succeeded: but the subsequent attempts to complete the connection failed."""
CYW43_LINK_BADAUTH = const(-3)
"""General failure code _before_ authentication. Check the supplied password."""

##
## Exceptions
##


class WirelessNetworkError(Exception):
    """
    General Wireless Network Exception. Thrown in response to one of the codes listed in the module `Attributes`, and originating from the underlying C library.

    The message of the the `Exception` is set to an appropriate response, and it should be assumed that the text of the `Exception` will be passed back to the user. Therefore it is important that the message aids further debugging without having to consult the underlying library documentation.
    """

    pass


##
## Functions
##


def netcode_to_str(error_code: int) -> str:
    """
    Converts the given wireless network error code to a short string, indicating the
    possible error. Note that no validation for sanity of the error code is
    attempted by this function. However the returned values are expected to be
    displayed directly to the user, and so should indicate (at least minimally)
    where further investigation might be helpful.
    """
    if error_code == CYW43_LINK_DOWN:
        return "The wireless link is unavailable - check the SSID is correct"
    elif error_code == CYW43_LINK_JOIN:
        return "The SSID or password is incorrect  - check the SSID and password."
    elif error_code == CYW43_LINK_NOIP:
        return (
            "The join request was successful, but no IP address was returned - check"
            " the DHCP settings for the specified SSID"
        )
    elif error_code == CYW43_LINK_UP:
        return "Successfully joined, and an IP address was obtained from the network"
    elif error_code == CYW43_LINK_FAIL:
        return "The link specified by the SSID is unavailable for unknown reasons"
    elif error_code == CYW43_LINK_NONET:
        return (
            "The authentication likely succeeded: but the subsequent attempts to"
            " complete the connection failed"
        )
    elif error_code == CYW43_LINK_BADAUTH:
        return (
            "General failure code before authentication - check the supplied password."
        )
    else:
        return "Unknown error"


def wireless_enable(
    ssid: str, password: str, link_light: Union[int, str] = "WL_GPIO0"
) -> None:
    """
    Enable the default wireless interface, connecting to the networking using
    the specified `ssid` and `password`. Optionally also supply the name, or the pin
    number, of the GPIO pin to use as the `link_light`, which will be 'on' if the
    network connection succeeds (and 'off' otherwise).

    !!! danger "Clear Text Password"

        As with the default wireless library, the `password` **must** be supplied to
        this function in clear text. This presents a potential exposure risk
        of the `password`, and that risk should be mitigated by appropriate storage and
        handling of the password _before_ calling this function.

    Parameters
    ----------

    ssid: str
        The SSID of the network to connect to.
    password: str
        The plain text of the password needed by the wireless network.
    link_light: int or str, optional
        The name (if a `str`) or number (if an `int`) of the GPIO pin to use as
        the link light. If a connection succeeds, this GPIO Pin will be set 'high':
        otherwise 'low' on failure. Defaults to the on-board (user) LED of the Pico W.

    Raises
    ------

    NameError
        The name (`int` or `str`) for the `link_light` is invalid, and a `Pin` with this name cannot be created.
    WirelessNetworkError
        The network named `ssid` cannot be joined with the specified `password`. See the exact `msg` of the `Exception` to determine whether this is a temporary (and may be retried) or a permanent error.
    """

    # Set-up the link status LED
    try:
        if link_light is not None:
            link_status = Pin(link_light, Pin.OUT)
    except NameError:
        print("Cannot initialise the requested link pin")

    # Set-up the Wireless Driver
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Number of connection attempts
    # before a hard fail
    max_wait = 10

    while max_wait > 0:
        if wlan.status() == CYW43_LINK_UP:
            break

        max_wait -= 1
        print("waiting for connection...")
        time.sleep(1)

    # Handle connection error
    if wlan.status() != CYW43_LINK_UP:
        raise WirelessNetworkError(
            "Network connection attempt failed:"
            f" { netcode_to_str(wlan.status()) } (Code: {wlan.status()})"
        )
    else:
        print("Connected")
        print("IP: " + wlan.ifconfig()[0])

    # Display the link light if connected
    if wlan.status() == CYW43_LINK_UP:
        link_status.on()
    else:
        link_status.off()
