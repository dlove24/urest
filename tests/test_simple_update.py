"""
Tests of the `update` verb (HTTP POST method), using the simple server `urest.examples.simpleled.SimpleLED`

Run as: `py.test test_simple_update.py`
"""
import requests

IP_ADDRESS = "10.0.30.225"


def test_requests_update_check():
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
    r = requests.get(f"http://{ IP_ADDRESS }/green_led")
    assert True


def test_requests_update_init():
    """
    Test
    ----

    Attempt to reset the server back to the known (default) state. This is
    achieved by sending an HTTP `DELETE` method request to the server to return the
    `led` noun to the default state.

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check that the call to `test_requests_init_delete` was successful

    """
    r = requests.delete(f"http://{ IP_ADDRESS }/green_led")
    assert r.status_code == requests.codes.ok


def test_requests_update_init_check():
    """
    Test
    ----

    Check the noun is in the default state of `0`

    Expectation
    -----------

    **Pass**: The noun `led` has the value `0`, indicating a return to the default state

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check the results of the `urest.tests.test_requests_update_setup` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led")
    assert r.content == b'{"led": 0}'


def test_requests_update_on():
    """
    Test
    ----

    Attempt to toggle the current state, setting the noun 'led' to `1`

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made

    """
    state = {"led": 1}
    r = requests.post(f"http://{ IP_ADDRESS }/green_led", json=state)
    assert r.status_code == requests.codes.ok


def test_requests_update_on_check():
    """
    Test
    ----

    Check the noun has been set to the state value `1`

    Expectation
    -----------

    **Pass**: The noun `led` has the value `1`, the previous `test_requests_update_on` method succeeded

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check the results of the `urest.tests.test_requests_update_on` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led")
    assert r.content == b'{"led": 1}'


def test_requests_update_off():
    """
    Test
    ----

    Attempt to toggle the current state, setting the noun 'led' to `0`

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made

    """
    state = {"led": 0}
    r = requests.put(f"http://{ IP_ADDRESS }/green_led", json=state)
    assert r.status_code == requests.codes.ok


def test_requests_update_off_check():
    """
    Test
    ----

    Check the noun has been set to the state value `0`

    Expectation
    -----------

    **Pass**: The noun `led` has the value `0`, the previous `test_requests_update_off` method succeeded

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun('led', SimpleLED(28))` has been made
      * Check the results of the `urest.tests.test_requests_update_off` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led")
    assert r.content == b'{"led": 0}'
