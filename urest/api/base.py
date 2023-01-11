"""
Implements the 'Abstract' Base Class for all the nouns used by the
`urest.http.server.RESTServer` class in defining resources.


.. Note::
  MicroPython does not implement the
  [`abc` module](https://docs.python.org/3.10/library/abc.html) which provides
  language-level support for abstract base classes. Therefore the
  `urest.http.server.RESTServer` class checks the ancestors of the class
  passed as a resource for the API to ensure they derive from `urest.api.base.APIBase`.
  Any class which _does not_ have `urest.api.base.APIBase` as an ancestor will
  therefore **not** work as a valid resource.

  This also means that `urest.api.base.APIBase` is not a pure virtual ABC, and
  so implements a minimum set of methods which hold and manipulate resource state.
  However all methods such as `urest.api.base.APIBase.get_state` and
  `urest.api.base.APIBase.set_state` are expected to be overridden in working
  implementations.

Licence
-------

This module, and all included code, is made available under the terms of the MIT
Licence

> Copyright (c) 2022-2023 David Love

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


class APIBase:

    ##
    ## Constructor
    ##

    def __init__(self):
        """The Abstract Base Class for the nouns, used in the response from the server.

        This base class defines the minimum interface used in marshalling requests from
        the clients by the `urest.http.server.RESTServer` class. The API defined by the
        server consists of 'nouns' representing the resources defined by the sub-classes
        of this base class, and the methods which act upon those resources (which map to
        the 'verbs' of the HTTP requests made to the `urest.http.server.RESTServer` class.

        Where data is returned to the client by the, e.g by the `get_state` method, JSON
        will ultimately be used as the encoding format. Sub-classes do not need to
        implement the saving of the object state to the client: however to assist they
        should be aware of the type of the each `value` returned as part of a `key/value`
        pair in the `Dictionary`.

        When returning data to the client, the `value` of each entry in the `Dictionary`
        will attempt to be inferred using the normal Python type library. If the type can be
        identified, then an appropriate JSON type will be used: otherwise the `value` of that
        `Dictionary` entry will be returned as a string.

        .. Warning:: Data will be returned to the client 'as is'
            No further checking on the validity (or otherwise) of the content of
            the `Dictionary` will be undertaken past this point. Anything that appear to be in
            a valid `Dictionary` will be returned to the client. It is the module consumers
            responsibility to ensure the returned data follows the form expected by those clients.
        """

        self._state_attributes = []
        """ Holds the current state and attributes of the resource """

    ##
    ## State Manipulation Methods
    ##

    def get_state(self) -> dict:
        """Returns the state of the resource.

        Return the state of the resource, as defined by the sub-classes. By default
        this method will return the contents of the private `state_attributes` `Dictionary`
        to the client; assuming that `Dictionary` has been appropriately completed
        in the processing of the resource.

        Returns
        -------

        Dictionary
          A mapping of (key, value) pairs which defines the resource state to return to the
          client.
        """

        return self._state_attributes

    def set_state(self, state_attributes: dict):
        """Sets the full state of the resource.

        The exact mechanism for updating the internal state of the resource represented
        by sub-classes is implementation defined. By default this method expects the
        _full_ state to be represented by the `state_attributes` parameters; and by
        default the new state will be exactly as stated by the `Dictionary` passed in
        through `state_attributes`.

        Parameters
        ----------

        state_attributes: Dictionary
            A list of (key, value) pairs representing the _full_ state of the
            resource. No merging of state is undertaken, or attempted.
        """

        if state_attributes is not None and isinstance(state_attributes, dict):
            self._state_attributes = state_attributes
        else:
            self._state_attributes = []

    def update_state(self, state_attributes: dict):
        """Updates the state of the resource, using the 'key/value' pairs of the
        `Dictionary` in `state_attributes`.


        The exact mechanism for updating the internal state of the resource represented
        by sub-classes is implementation defined. By default this expects to update
        only part of the state through the use of the partial state defined in
        `state_attributes`. This defines a `Dictionary` of (key, value) pairs which
        can be interpreted by sub-classes to update the true internal state as needed.

        Parameters
        ----------

        state_attributes: Dictionary
            A list of (key, value) pairs representing the _partial_ state of the
            resource. The exact mechanism for merging this partial state if left
            to the implementation of the sub-classes.
        """

        if state_attributes is not None and isinstance(state_attributes, dict):
            for key in state_attributes:
                try:
                    self._state_attributes[key] = state_attributes[key]
                except KeyError:
                    self._state_attributes[key] = None
        else:
            self._state_attributes = []

    def delete_state(self):
        """Removes the internal state of the resource, essentially 'resetting' or
        re-initialising the object.

        The exact mechanism for returning the state to the defaults are left to
        the implementation. However it is expected that once this call completes
        the internal state will be _identical_ to that of the default constructor.
        """

        self._state_attributes = []
