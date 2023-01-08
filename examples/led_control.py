"""
An example of a small application which control a single GPIO pin.

Overview
--------

This examples export a single noun, `led`, which is used to set, test and otherwise control a single GPIO pin. It can be used an example of a the way in which this API class can be used, along with the definition of the  `urest.examples.simpleled.SimpleLED` class.

To use this example, the variables `SSID` and `PASSWORD` must also be defined, and set to suitable values for the local network. Space for these variables has been provided at the start of the '`main`' loop. The code will then attempt to create an API server on the _network_ side of the machines local interfaces, bound to port 80.

.. Note:: MicroPython Includes

    This module as presented has a number of `try..finally` blocks which exist to
    catch uses of this code where the standard MicroPython libraries are not
    available. If _known_ to be running under MicroPython, or suitably adapted,
    these can be removed.

.. Warning:: Exposed Network Ports

    This code _does not_ attempt to take any defensive stances with respect
    to the network environment, beyond the normal measures in the API code.
    As is normal for MicroPython implementations, it also assumes the SSID
    and the network password are embedded in the code, and therefore exposed.
    Careful review of the application code, and the network environment, should
    be undertaken before this code is used in anything other than a benign
    environment under _total_ control of the developer.

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W

Licence
-------

This code, and all included code, is made available under the terms of the MIT Licence

> Copyright 2021--2022 (c) Erik de Lange, Copyright (c) 2022--2023 David Love

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

import time

try:
    from machine import Pin
    from micropython import const

    import network
    import uasyncio as asyncio
except ImportError:
    print("Ignoring MicroPython includes")

from urest.http import RESTServer
from urest.api import APIBase
from urest.examples.simpleled import SimpleLED

###
### Main Loop
###

# Set the SSID of the wireless network
SSID = "SSID"
# Set the password of the wireless network
PASSWORD = "PASSWORD"

# Set-up the link status LED
try:
    link_status = Pin("WL_GPIO0", Pin.OUT)
except NameError:
    print("Cannot find the MicroPython PIN library")

try:
    # Set-up the Wireless Driver
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Number of connection attempts
    # before a hard fail
    max_wait = 10

    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            print("Already connected!")
            print("IP:  " + wlan.ifconfig()[0])
            break

        max_wait -= 1
        print("waiting for connection...")
        time.sleep(1)

        print(wlan.status())

        # Handle connection error
        if wlan.status() != 3:
            raise RuntimeError("network connection failed")
        else:
            print("Connected")
            print("IP: " + wlan.ifconfig()[0])

    # Display the link light if connected
    if wlan.status() == 3:
        link_status.on()
    else:
        link_status.off()

except NameError:
    print("Cannot find the MicroPython network library")

# Create the server ...
app = RESTServer()

# ... and register the nouns
try:
    app.register_noun("led", SimpleLED(0))
except NameError:
    print("Cannot find the MicroPython PIN library")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
