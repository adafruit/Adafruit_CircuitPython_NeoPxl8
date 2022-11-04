# SPDX-FileCopyrightText: 2016 Damien P. George
# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
# SPDX-FileCopyrightText: 2019 Roy Hooper
# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: MIT

"""
`adafruit_neopxl8` - Neopixel strip driver using RP2040's PIO
====================================================

* Author(s): Damien P. George, Scott Shawcroft, Carter Nelson, Roy Hooper, Jeff Epler
"""

import adafruit_pioasm
import bitops
import adafruit_pixelbuf
import rp2pio

_PROGRAM = """
.program piopixl8
.side_set 2
; NeoPixels are 800kHz bit streams.  Zeros are 1/3 duty cycle and ones are 2/3 duty cycle.
; 1 loop = 6 cycles, so the PIO peripheral needs to run at 1.2MHz.
; x must be pre-loaded with zero so we can set all-ones (with mov pins, !x)
; or all-zeros (with mov pins, x)
    pull ifempty ; don't start outputting HIGH unless data is available
    mov pins, ~ x [1]; always-high part
    out pins, 8 [1] ; variable part
    mov pins, x ; always-low part (2nd cycle is the 'pull ifempty' after wrap)
"""

_ASSEMBLED = adafruit_pioasm.assemble(_PROGRAM)

# Pixel color order constants
RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"
"""Green Red Blue White"""


class NeoPxl8(adafruit_pixelbuf.PixelBuf):
    """
    A sequence of neopixels.

    :param ~microcontroller.Pin data0: The first of 8 data registers, in GPIO order
    :param int n: The total number of neopixels.  Must be a multiple of the number of strands.
    :param int num_strands: The number of neopixels in each strand.
    :param int bpp: Bytes per pixel. 3 for RGB and 4 for RGBW pixels.
    :param float brightness: Brightness of the pixels between 0.0 and 1.0 where 1.0 is full
      brightness
    :param bool auto_write: True if the neopixels should immediately change when set. If False,
      `show` must be called explicitly.
    :param str pixel_order: Set the pixel color channel order. GRB or GRBW is
      set by default, depending on bpp.

    Example for Adafruit Feather RP2040 Scorpio, sets 240 LEDs in 8 strands to faint red:

    .. code-block:: python

        pixels = adafruit_neopxl8.NeoPxl8(board.NEOPIXEL0, 8*30, num_strands=8, auto_write=False)
        pixels.fill(0x010000)
        pixels.show()

    .. py:method:: NeoPxl8.show()

        Shows the new colors on the pixels themselves if they haven't already
        been autowritten.

    .. py:method:: NeoPxl8.fill(color)

        Colors all pixels the given ***color***.

    .. py:attribute:: brightness

        Overall brightness of the pixel (0 to 1.0)

    """

    def __init__(
        self,
        data0,
        n,
        *,
        num_strands=8,
        bpp=3,
        brightness=1.0,
        auto_write=True,
        pixel_order=None,
    ):
        if n % num_strands:
            raise ValueError("Length must be a multiple of num_strands")
        if not pixel_order:
            pixel_order = GRB if bpp == 3 else GRBW
        else:
            if isinstance(pixel_order, tuple):
                order_list = [RGBW[order] for order in pixel_order]
                pixel_order = "".join(order_list)

        super().__init__(
            n, brightness=brightness, byteorder=pixel_order, auto_write=auto_write
        )

        self._transposed = bytearray(bpp * n * 8 // num_strands)
        self._num_strands = num_strands

        self._sm = rp2pio.StateMachine(
            _ASSEMBLED,
            frequency=800_000 * 6,
            first_out_pin=data0,
            out_pin_count=8,
            first_set_pin=data0,
            auto_pull=True,
            out_shift_right=False,
            pull_threshold=8,
        )

    def deinit(self):
        """Blank out the neopixels and release the state machine."""
        self.fill(0)
        self.show()
        self._sm.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    @property
    def n(self):
        """
        The total number of neopixels in all strands (read-only)
        """
        return len(self)

    @property
    def num_strands(self):
        """
        The total number of neopixels in all strands (read-only)
        """
        return self._num_strands

    def _transmit(self, buffer):
        bitops.bit_transpose(buffer, self._transposed, self._num_strands)
        self._sm.write(self._transposed)
