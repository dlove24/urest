"""
Tests of the `get` verb (HTTP GET method), using the simple server `urest.examples.pwmled.PWMLED`.

Run as: `py.test test_simple_get.py`
"""
import requests

IP_ADDRESS = "10.0.30.220"


def test_pwm_get_check():
    """
    Test
    ----.

    Check for basic connection to the server. The URI is given, but for
    this test the response is not checked.

    .. NOTE:: Connection Check

    If this test fails, the most likely cause is that the `IP_ADDRESS` is
    incorrect, _or_ that the test server in `urest.examples.pwmled.PWMLED`
    is not running on the MicroPython board. **Double-check** both the
    test preconditions if this test fails and before investigating further.

    Expectation
    -----------

    **Pass**: Successful request made to the server with the requested URI

    On-Failure
    ----------

      * Check that `IP_ADDRESS` is correct
      * Check the `urest.examples.pwmled.PWMLED` is running
      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", PWMLED(1))` has been made

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.status_code == requests.codes.ok


def test_pwm_get_setup():
    """
    Test
    ----.

    Ensures the test server is in the known (default) state required for further tests. This is achieved by sending an HTTP `DELETE` method request to the
    server to return the `green_led0` noun to the default state.

    .. NOTE::

    This test may fail if the `DELETE` verb is handled incorrectly (not returning the noun to the initial state) **or** because the `GET` verb is handled incorrectly. Therefore the results of the `test_simple_delete` test runner should also be taken into consideration when interpreting failure.

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", PWMLED(1))` has been made

    """
    r = requests.delete(f"http://{ IP_ADDRESS }/green_led0")
    assert r.status_code == requests.codes.ok


def test_pwm_get_data():
    """
    Test
    ----.

    Check the noun has been returned to the default state of `current == 0`

    Expectation
    -----------

    **Pass**: The noun `green_led0` has the value `current == 0`, indicating a return to the default state

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", PWMLED(1))` has been made
      * Check the results of the `test_pwm_get_setup()` method, to ensure the noun was initialised correctly

    """
    r = requests.get(f"http://{ IP_ADDRESS }/green_led0")
    assert r.content == b'{"current": 0,"desired": 0}'


def test_pwm_set_on():
    """
    Test
    ----.

    Attempt to set the noun 'led' to `1`

    Expectation
    -----------

    **Pass**: HTTP Return code 200, indicating success

    On-Failure
    ----------

      * Check that a call to `urest.http.server.RESTServer.register_noun`, e.g. `app.register_noun("green_led0", PWMLED(1))` has been made

    """
    state = {"led": 1}
    r = requests.put(f"http://{ IP_ADDRESS }/green_led0", json=state)
    assert r.status_code == requests.codes.ok
