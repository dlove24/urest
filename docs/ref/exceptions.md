# Library Exceptions

Library-specific `Exception` classes. Provides clients with more granular
exception handling facilities, allowing a clearer response to specific
internal or external (network) failures.

## Server Exceptions

The following exceptions are thrown by the [`urest.http.server.RESTServer`][urest.http.server.RESTServer] class, and should be handled by the _API server_ and not passed directly onto the network client.

::: urest.http.server.RESTClientError
          options:
            heading_level: 3

::: urest.http.server.RESTServerError
          options:
            heading_level: 3

::: urest.http.server.RESTParseError
          options:
            heading_level: 3

## Network Helper Exceptions

The following exceptions arise from the [`urest.utils`][urest.utils] module. Unless the classes and functions within the [`urest.utils`][urest.utils] module are being used, these can be ignored as they _should not_ be generated by the core library modules.

::: urest.utils.network_connect.WirelessNetworkError

