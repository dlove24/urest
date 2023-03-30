# Setting Up the Pi Pico

!!! info "What you will need"

    * Pico H or Pico W
    * Mico-USB cable
    * Windows or Linux PC
    * Pimoroni Pico Explorer Base (optional)
    * Breadboard for mounting the Pico (optional)

## Introduction

This How-To covers the installation of [MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#what-is-micropython) on the [Raspberry Pi Pico](https://www.raspberrypi.com/documentation/microcontrollers/). It is oriented around the [Pimoroni Pico Explorer Base](https://shop.pimoroni.com/products/pico-explorer-base), but will also work for the bare-bones Pico H and Pico W boards.

## Installing Micro Python

The _Explorer_ boards we have the Pico's installed onto need a custom version of the MicroPython firmware to enable all of the various breakout features. For consistency we use the same version of firmware on the bare Pico Boards as well.

!!! note

    If in doubt, select the firmware version for the Pico W: this will work for both the wireless _and_ non-wireless Pico's. This makes it less likely you will accidentally download a non-working version to the Pico W's.

1. The full set of releases is available on [GitHub](https://github.com/pimoroni/pimoroni-pico/releases/). We recommend [`pimoroni-pico-v1.19.14-micropython`](https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.19.14) as a stable reference version. Select the relevant version of the Pico firmware, and download to somewhere convenient

   - **Pico H** (non-wireless version): [https://github.com/pimoroni/pimoroni-pico/releases/download/v1.19.14/pimoroni-pico-v1.19.14-micropython.uf2](https://github.com/pimoroni/pimoroni-pico/releases/download/v1.19.14/pimoroni-pico-v1.19.14-micropython.uf2)

   - **Pico W** (wireless version): [https://github.com/pimoroni/pimoroni-pico/releases/download/v1.19.14/pimoroni-picow-v1.19.14-micropython.uf2](https://github.com/pimoroni/pimoroni-pico/releases/download/v1.19.14/pimoroni-picow-v1.19.14-micropython.uf2)

2. Next put the Pico into _bootloader mode_ so that we can install the firmware. Make sure the USB cable is unplugged, then hold down the `BOOTSEL` button on the Pico whilst plugging the USB cable back in.

   - **Windows** should recognise the Pico as a USB drive, and add a `D:` to the machine. If this doesn't happen, you may need to repeat the procedure.

   - **Linux** should recognise the Pico as a USB drive, and for most desktops should mount the drive for you. If this doesn't happen, you may need to manually mount the device.

3. Copy the firmware to the USB drive. After a few seconds the copy should finish and the Pico will reboot and will start the MicroPython interpreter on the Pico.

!!! note

    For a bare Pico, there will be little sign of success by default: except that the USB drive should disappear. On the Pico Explorer boards the OLED back-light should turn on. However if the Python IDE cannot connect to the Pico, repeat this step.

## Installing a Python IDE (Thonny)

!!! warning "Check You are Installing to a Local Drive"

    Thonny **does not** like running from a network drive (e.g. `P:` in the labs) so the recommendation is to create a folder on your OneDrive and unpack the `.zip` file there. If you get permission errors, _double-check_ you are running from a local folder or OneDrive and _not_ somewhere else.

!!! warning "Don't Run from the .zip File"

    You **cannot** run Thonny from _inside_ the .zip file: so you cannot just double-click the downloaded file. Instead you **must** extract the .zip file to run the contents from a normal folder.

1. We now need to talk to the Pico, using [Thonny](https://thonny.org) as the IDE. Thonny will install Python, an IDE, the Pico SDK and the interface to the serial driver for the Pico all in one package. We are using the _portable_ version, which you can [download from the offical site](https://github.com/thonny/thonny/releases/download/v4.0.1/thonny-4.0.1-windows-portable.zip) or the module website.

2. Start the Thonny IDE: this may take some time if downloading from OneDrive.

3. If everything is working it should show a connection to the '`MicroPython (Raspberry Pi Pico)`' in the bottom right of the Thonny IDE window. In addition you should see the Python prompt: '`>>>`' and a message telling you which version of MicroPython we are running.
