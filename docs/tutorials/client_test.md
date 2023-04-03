# A Simple Echo Server (Windows, Linux and Mac)

!!! info "What you will need"

    * Pico W, with `urest` installed [for the server]
    * Mico-USB cable
    * A wireless network, with a known SSID and password
    * Windows, Linux or Mac command line with [`curl`](https://curl.se/download.html) installed

This tutorial aims to get a working development environment for the _clients_ of the `urest` library. We will also install a minimal 'echo' server to test the client against, and make sure all of the set-up steps are working.

!!! note "Pick You Platform"
    'Step 1' below is deliberately repeated, as the steps required _will_ be different for Windows and Linux/Mac platforms. Pick the relevant version of 'Step 1' for your platform, and then continue to 'Step 2'.

## Step 1A: Setting Up (Linux and Mac)

To make life easier, we will use a _virtual environment_ so that your test Python environment does not conflict with the version on the system you are using.

1. Create the virtual environment in the _current_ directory, installed into the '`.venv`' sub-directory, by typing

    ```
    python3 -m venv .venv
    ```

2. Activate the virtual environment, which will ensure we don't install anything into the core system

    ```
    source .venv/bin/activate
    ```

3. Now install the '`urest`' library

    ```
    pip install urest_mp
    ```

!!! note
    In the future you don't need to install the '`urest`' library: but you will have to activate the virtual environment each time by moving into the sub-directory you are using and then typing "`python3 -m venv .venv`". This ensures that your test environment stays distinct from the system Python environment, and doesn't cause any conflicts.

## Step 1B: Setting Up (Windows)

To make life easier, we will use a _virtual environment_ so that your test Python environment does not conflict with the version on the system you are using.

1. Create the virtual environment in the directory you want to use by typing

    ```
    python -m venv c:\path\to\myenv
    ```

    This assumes that the '`python`' interpreter is in your `PATH`: if not you will need to specify the exact location of the '`python`' interpreter as well.

2. Activate the virtual environment, which will ensure we don't install anything into the core system

    ```
    c:\path\to\myenv\Scripts\activate.bat
    ```

    If you are using PowerShell as the running environment, then you may need

    ```
    c:\path\to\myenv\Scripts\Activate.ps1
    ```

3. Now install the '`urest`' library

    ```
    pip install urest_mp
    ```

4. Once Python is running, with the virtual environment set-up, you will also need a copy of the '`curl`' utility. Download a copy of this from the [curl website](https://curl.se/download.html), and make sure this utility is in your path (it should be once the install completes).

!!! note

    In the future you don't need to install the '`urest`' library: but you will have to activate the virtual environment each time by using the script or batch from from (2). This ensures that your test environment stays distinct from the system Python environment, and doesn't cause any conflicts.

## Step 2: A Simple Server

We will create a very simple server _on the Pico W_, which relies on the '`EchoServer`' class written as part of the '`urest`' library. You will also need your wireless network SSID and password, so that the Pico W can act as a server for the test client we will create in Step 3.

1. Create a file on the Pico W using an editor or IDE (e.g. Thonny) which is called '`echo_test.py`', with the following content

      ```python
      import time
      import urest.utils

      try:
         import uasyncio as asyncio
      except ImportError:
         import asyncio

      from urest.http import RESTServer
      from urest.api import APIBase
      from urest.examples.echo import EchoServer

      ###
      ### Connect to the Wireless network
      ###

      urest.utils.wireless_enable("SSID", "PASSWORD")

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
      ```

2. Change the `SSID` and `PASSWORD` for the `urest.utils.wireless_enable` function to reflect the values for _your network_.

3. Save the file, and then try to run the code. You may be able run the code in your IDE (e.g. Thonny), or use the command

      ```
      python echo_test.py
      ```

      This should give some output resembling the following

      ```
      Connected
      IP: 192.0.2.220
      SERVER: Started on 0.0.0.0:8024
      ```

      If you _don't_ get the line '`Connected`', **double-check** the password and the SSID supplied are correct. Equally if you don't see a line starting '`IP:`', double-check that everything is working _before_ you move on.

4. Make a note of the IP address. Now _leave the server code running on the Pico W for the next step_

## Step 3: Testing the Server

On the _client_, and inside the virtual environment set-up earlier, we will now run `curl` to connect to the Pico W acting as a server.

!!! note "Check Your Shell"
      For our arguments to '`curl`' we are using single quotes ('`'`') _and not_ double quotes ('`"`'). You will find that some shells (including Windows) will modify the arguments so that '`curl`' _does not_ send the right arguments to the client. If you must use double quotes, the '`curl`' command need to change to escape the internal double quote, e.g. '`curl -X PUT -d "{\"echo\":0}" -H "Content-Type: application/json" http://localhost:8024/echo`'.

1. Using the IP address you noted down earlier, the server should respond to the following command from the client

      ```
      curl http://192.0.2.220:8024/echo
      ```

      with the output

      ````
      {"echo": "False"}
      ````

2. Now we will try to change the state of the server from the client. Again using your own IP address, try

      ```
      curl -X PUT -d '{"echo":1}' -H "Content-Type: application/json" http://192.0.2.220:8024/echo
      ```

      and repeat the command

      ```
      curl http://192.0.2.220:8024/echo
      ```

      What is the output, now? Hopefully you should see a difference between the two commands, and should be able to change the server state, so that the server now responds with

      ````
      {"echo": "True"}
      ````

      If this works, we know the server is working, and we can start to build our own clients.
