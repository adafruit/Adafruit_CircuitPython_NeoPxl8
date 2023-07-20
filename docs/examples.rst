Examples
===========

.. contents:: 

Simple Test
-----------

Ensure your device works with this simple test.

.. literalinclude:: ../examples/neopxl8_simpletest.py
    :caption: examples/neopxl8_simpletest.py
    :linenos:

Animations
-----------

Next, try some Adafruit animations. Here is the example program, which will run the
``Comet()`` animation on up to 8 neopixel strips from one `Feather Scorpio RP2040 <https://www.adafruit.com/product/5650>`_.

.. literalinclude:: ../examples/neopxl8_animations.py
    :caption: examples/neopxl8_animations.py
    :linenos:

Adafruit LED Animation Functions
--------------------------------

There are a variety of animations you can use (Pulse, Chase, Rainbow, RainbowChase, etc.).

Below are code snippets that you can test in the ``neopxl8_animations.py`` file. **NOTE** I
am only including code snippets of the required import statement and the function call.

The Blink() function
********************

Blink a color on and off.

.. code-block:: python
    :emphasize-lines: 2, 5

    # import the function
    from adafruit_led_animation.animation.blink import Blink

    # Call the Blink() function
    Blink(strand, 0.1, (0, 255, 120))

**Blink() Parameters:**

:pixel_object: The initialised LED object.
:speed: Animation speed in seconds, e.g. ``0.1``.
:color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
:name=None: *[Optional] string to represent the name of the function.*

The Chase() function
***********************

Chase pixels in one direction in a single color, like a theater marquee sign.

.. code-block:: python
    :emphasize-lines: 2, 5

    # import the function
    from adafruit_led_animation.animation.chase import Chase

    # Call the Chase() function
    Chase(strand, 0.1, (0, 255, 120), size=1, spacing=2, reverse=True)

**Chase() Parameters:**

:pixel_object (adafruit_neopxl8.NeoPxl8): The initialised LED object.
:speed: Animation speed rate in seconds, e.g. ``0.1``.
:color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
:size=2: *[Optional] Number of pixels to turn on in a row*
:spacing=3: *[Optional] Number of pixels to turn off in a row.*
:reverse=False: *[Optional] Reverse direction of movement.*
