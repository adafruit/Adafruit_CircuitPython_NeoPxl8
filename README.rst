Introduction
============


.. image:: https://readthedocs.org/projects/neopxl8/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/neopxl8/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_neopxl8/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_neopxl8/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

PIO-driven 8-way concurrent NeoPixel driver for RP2040


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `pioasm <https://github.com/adafruit/Adafruit_CircuitPython_pioasm>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_neopxl8

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

See the `Examples page <examples.html>`_ for a full example.  This example shows how to set up 8 30-pixel LED strands on an Adafruit Feather Scorpio RP2040 and set them all to dim red:

.. code-block:: python

    import time
    import board
    from adafruit_neopxl8 import NeoPxl8

    # Customize for your strands here
    num_strands = 8
    strand_length = 30
    first_led_pin = board.NEOPIXEL0

    num_pixels = num_strands * strand_length

    # Make the object to control the pixels
    pixels = NeoPxl8(
        first_led_pin,
        num_pixels,
        num_strands=num_strands,
    )

    pixels.fill(0x01_00_00)

    while True:
        time.sleep(1)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/neopxl8/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_neopxl8/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
