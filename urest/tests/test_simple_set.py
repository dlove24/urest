"""
Tests of the `set` verb (HTTP PUT method), using the simple server `urest.examples.simpleled.SimpleLED`

Run as: `py.test test_simple_set.py`
"""
import requests

IP_ADDRESS = "10.0.30.225"


def test_requests_set_check():
    """
    Test
    ----

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
      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.status_code == requests.codes.ok


def test_requests_set_on():
    """
    Test
    ----

    Attempt to set the noun 'led' to `1`

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made

    """
    state = {"led": 1}
    r = requests.put(f"http://{ IP_ADDRESS }/green_led0", json=state)
    assert r.status_code == requests.codes.ok


def test_requests_set_on_check():
    """
    Test
    ----

    Check the noun has been set to the state value `1`

    Expectation
    -----------

    **Pass**: The noun `led` has the value `1`, the previous `test_requests_set_on()` method succeeded

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check the results of the `test_requests_set_on()` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.content == b'{"led": 1}'


def test_requests_set_off():
    """
    Test
    ----

    Attempt to set the noun 'led' to `0`

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made

    """
    state = {"led": 0}
    r = requests.put(f"http://{ IP_ADDRESS }/green_led0", json=state)
    assert r.status_code == requests.codes.ok


def test_requests_set_off_check():
    """
    Test
    ----

    Check the noun has been set to the state value `0`

    Expectation
    -----------

    **Pass**: The noun `led` has the value `0`, the previous `test_requests_set_off()` method succeeded

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check the results of the `test_requests_set_off()` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.content == b'{"led": 0}'
