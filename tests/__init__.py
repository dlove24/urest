"""
Test scripts for checking the library functionality.

Overview
--------

This module describes a number of tests, designed to be run under the
[PyTest](https://docs.pytest.org/en/7.2.x/contents.html) harness. Nearly all
tests also require the [requests](https://requests.readthedocs.io/en/latest)
library to be installed, and will also require network access.

To enable simple repeat testing of specific failures, the
[`pytest-curl-report`](https://pypi.org/project/pytest-curl-report/) plugin is
also strongly recommended. This also makes it easier run specific tests outside
the test scripts.

All tests in this folder should be follow the standard PyTest rules for test
discovery so that running

```
$ py.test
```

will run all tests.

Each test is standalone, so that running

```
$ py.test simple_get.py
```

inside the `tests` folder should run the desired tests. Specific tests can also
be run programmaticaly through this module. Consult the PyTest documentation for
details.

Running the Tests
-----------------

These tests depend on the server described in
`urest.examples.simpleled.SimpleLED` being run on the MicroPython board. That
board **must** be network accessible to the machine on which the test harness is
being run.

Once the MicroPython board is running the example server code, the IPv4 address
of that board must then be used to modify the test scipts. All scripts make
reference to an IPv4 address in the variable `IP_ADDRESS` at the start of the
script: put the **real** IP address of the board under test in here **before**
running the test.

.. NOTE:: Check Connectivity First

  The first test script is _always_ a connection check. If this connection test fails, **double-check** the board is accessible and that `IP_ADDRESS` is correct
  before going further. Otherwise the results of the test scripts are likely to be
  misleading...

Tested Implementations
----------------------

This version is written for MicroPython 3.4, and has been tested on:

  * Raspberry Pi Pico W

Licence
-------

This module, and all included code, is made available under the terms of the MIT Licence

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
