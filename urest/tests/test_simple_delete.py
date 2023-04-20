"""
Tests of the `delete` verb (HTTP DELETE method), using the simple server `urest.examples.simpleled.SimpleLED`.

Run as: `py.test test_simple_delete.py`
"""
import requests

IP_ADDRESS = "10.0.30.220"


def test_requests_delete_check():
    """
    Test
    ----.

    Check for basic connection to the server. The URI is given, but for
    this test the response is not checked.

    .. NOTE:: Connection Check

    If this test fails, the most likely cause is that the `IP_ADDRESS` is
    incorrect, _or_ that the test server in `urest.examples.simpleled.SimpleLED`
    is not running on the MicroPython board. **Double-check** both the
    test preconditions if this test fails and before investigating further.

    Expectation
    -----------

    **Pass**: Successful request made to the server with the requested URI

    On-Failure
    ----------

      * Check that `IP_ADDRESS` is correct
      * Check the `urest.examples.simpleled.SimpleLED` is running
      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", SimpleLED(1))` has been made

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.status_code == requests.codes.ok


def test_requests_init_delete():
    """
    Test
    ----.

    Attempt to set the noun `green_led0` to `1`, to allow checking of the next
    `DELETE` request

    Expectation
    -----------

    **Pass**: The noun `green_led0` processes the request with a HTTP return code of 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", SimpleLED(1))` has been made

    """
    state = {"led": 1}
    r = requests.put(f"http://{ IP_ADDRESS }/green_led0", json=state)
    assert r.status_code == requests.codes.ok


def test_requests_try_delete():
    """
    Test
    ----.

    Attempt to reset the server back to the known (default) state. This is
    achieved by sending an HTTP `DELETE` method request to the server to return the
    `green_led0` noun to the default state.

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", SimpleLED(1))` has been made
      * Check that the call to `test_requests_init_delete()` was successful

    """
    r = requests.delete(f"http://{ IP_ADDRESS }/green_led0")
    assert r.status_code == requests.codes.ok


def test_requests_check_delete():
    """
    Test
    ----.

    Check the noun has been returned to the default state of `0`

    Expectation
    -----------

    **Pass**: The noun `green_led0` has the value `led: 0`, indicating a return to the default state

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", SimpleLED(1))` has been made
      * Check the results of the `test_requests_init_delete()` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.content == b'{"led": 0}'
