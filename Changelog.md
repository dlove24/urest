# Releases

All releases should be on [PyPi](https://pypi.org/project/urest-mp), and also published on [GitHub](https://github.com/dlove24/urest). A full log of the changes can be found in the source, or on GitHub: what follows is a summary of key features/changes.

## 2023-04-03: urest 0.2.8

### New

- Added a `urest.utils` library for code which assists in developing clients and servers. Currently this is reasonably minimal, with a helper function for connecting to wireless networks.

### Changed

- Documentation moved from `pdoc3` to `mkdocs` as the official generator, and now hosted on [Read The Docs](https://urest.readthedocs.io/).
- Increase conformity with the HTTP/1.1 specification by consistently terminating all lines with '`\r\n`' in response to the client requests.  

