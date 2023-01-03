# Background

This is a simple HTTP server, specialised to the delivery of a REST-like API instead of a general HTTP server. The design, and the use of the `asyncio` library, is inspired by the [MicroPython HTTP Server](https://github.com/erikdelange/MicroPython-HTTP-Server) by Erik de Lange. This library uses a roughly similar structure for the core of the `asyncio` drivers, and especially in the `HTTPResponse` class. Differences include

* A more object-oriented design of the call/response handler, made easier this library is _not_ a general HTTP server. For instance Python `getters` and `setters` are used where possible for input validation, and the central API response is based on the `APICall` abstract base class

* A more explicit validation of input from the network layer, especially in the assumption that all input is by default hostile. This library should serve as an example of best-practice in protocol handling; at least in the slightly resource constrained environment of MicroPython

* This implementation is principally a teaching library, so the documentation should be at least as important as the 'code'. Where possible all algorithms and implementation techniques should also be explained as fully as possible, or at least linked to reference standards/implementations.

* For consistency, all code should also be in the format standardised by the [Black][https://github.com/psf/black) library. This makes it easier to co-ordinate external code and documentation with the implementation documented here.

# Known Implementations

* Raspberry Pi Pico W (MicroPython 3.4)
