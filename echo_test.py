import time

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from urest.http import RESTServer
from urest.api import APIBase
from urest.examples.echo import EchoServer

###
### Main Loop
###

# Create the server ...
app = RESTServer(port=8024)

# ... and register the nouns
try:
    app.register_noun("echo", EchoServer())
except NameError:
    print("Cannot initalise the API")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(app.start())
    loop.run_forever()
