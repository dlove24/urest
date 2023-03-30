# Running The Test Scripts For Checking the Library Functionality

!!! info "What you will need"

    * Pico H or Pico W running the Test Server
    * Windows or Linux PC

## Overview

This module describes a number of tests, designed to be run under the [PyTest](https://docs.pytest.org/en/7.2.x/contents.html) harness. Nearly all tests also require the [requests](https://requests.readthedocs.io/en/latest) library to be installed, and will also require network access.

To enable simple repeat testing of specific failures, the [`pytest-curl-report`](https://pypi.org/project/pytest-curl-report/) plugin is also strongly recommended. This also makes it easier run specific tests outside the test scripts.

All tests in this folder should be follow the standard PyTest rules for test discovery so that running

```
$ py.test
```

will run all tests.

Each test is standalone, so that running

```
$ py.test simple_get.py
```

inside the `tests` folder should run the desired tests. Specific tests can also be run programmaticaly through this module. Consult the PyTest documentation for details.

## Running the Tests

These tests depend on the server described in `urest.examples.simpleled.SimpleLED` being run on the MicroPython board. That board **must** be network accessible to the machine on which the test harness is being run.

Once the MicroPython board is running the example server code, the IPv4 address of that board must then be used to modify the test scipts. All scripts make reference to an IPv4 address in the variable `IP_ADDRESS` at the start of the script: put the **real** IP address of the board under test in here **before** running the test.

!!! note "Check Connectivity First"

    The first test script is _always_ a connection check. If this connection test fails, **double-check** the board is accessible and that `IP_ADDRESS` is correct before going further. Otherwise the results of the test scripts are likely to be misleading...
