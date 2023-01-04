"""
Micro HTTP server dedicated to REST-style API Requests. Inspired by the
[MicroPython HTTP Server](https://github.com/erikdelange/MicroPython-HTTP-Server)
by Erik de Lange, as a simple consumer of the Python 3 `asyncio` library for the
low-level socket handling and use of co-routines to simplify request handling.

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W


Standards
---------

  * For HTTP/1.1 specification see: https://www.ietf.org/rfc/rfc2616.txt

Licence
-------

This module, and all included code, is made available under the terms of the MIT
Licence

> Copyright 2022 (c) Erik de Lange, Copyright (c) 2022-2023 David Love

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

# Import the Metaclass for Abstract Base Classes
from abc import ABC, abstractmethod


class APIBase(ABC):

    ##
    ## Constructor
    ##

    def __init__(self):
        """The Abstract Base Class for the nouns, used in the response from the server.

        This base class defines the minimum interface used in marshalling requests from
        the clients by the `urest.http.server.RESTServer` class. The API defined by the
        server consists of 'nouns' representing the resources defined by the sub-classes
        of this base class, and the methods which act upon those resources.
        """

        _state_attributes = []
        """ Holds the current state and attributes of the resource """

    ##
    ## State Manipulation Methods
    ##

    @abstractmethod
    def get_state(selector=[]):
        """Returns the state of the resource, optionally confined to the context stated
        by the `selector`.

        Return the state of the resource, as defined by the sub-classes. By default
        this method will return the contents of the private `state_attributes` dictionary
        to the client; assuming that dictionary has been appropriately completed
        in the processing of the resource.

        Parameters
        ----------

        selector: dict
            An optional list of (key, value) pairs which the method may use to return
            only a sub-set of the resource state represented by this class.

        Returns
        -------

        dict
          A mapping of (key, value) pairs which defines the resource state to return to the
          client. Each 'key' of the dictionary will be returned to the client on a separate
          line in the HTTP body: with the value converted to a string using the normal Python
          coercion methods.

          .. Warning:: Data will be returned to the client 'as is'
            No further checking on the validity (or otherwise) of the content of
            the dictionary will be undertaken past this point. Anything that appear to be in
            a valid dictionary will be returned to the client. It is the module consumers
            responsibility to ensure the returned data follows the form expected by those clients.
        """

        return self._state_attributes

    @abstractmethod
    def set_state(self, state_attributes, selector=[]):
        """Updates the state of the resource, optionally only updating the sub-state(s)
        set by the `selector`.

        The exact mechanism for updating the internal state of the resource represented
        by sub-classes is implementation defined. By default this method expects the
        _full_ state to be represented by the `state_attributes` parameters; and by
        default the new state will be exactly as stated by the dictionary passed in
        through `state_attributes`.

        A sub-class may, though, choose to update only part of the state through the
        use of the `selector`. This defines a dictionary of (key, value) pairs which
        can be interpreted by sub-classes as needed.

        Parameters
        ----------

        state_attributes: dict
            A list of (key, value) pairs representing the _full_ state of the
            resource. No merging of state is undertaken, or attempted.

        selector: dict
            An optional list of (key, value) pairs which the method may use to return
            only a sub-set of the resource state represented by this class.

        Returns
        -------

        dict
          A mapping of (key, value) pairs which defines the resource state to return to the
          client. Each 'key' of the dictionary will be returned to the client on a separate
          line in the HTTP body: with the value converted to a string using the normal Python
          coercion methods.

          .. Warning:: Data will be returned to the client 'as is'
            No further checking on the validity (or otherwise) of the content of
            the dictionary will be undertaken past this point. Anything that appear to be in
            a valid dictionary will be returned to the client. It is the module consumers
            responsibility to ensure the returned data follows the form expected by those clients.
        """

        if state_attributes is not None and isinstance(state_attributes, dict):
            self._state_attributes = state_attributes
        else:
            self._state_attributes = []
