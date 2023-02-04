# SPDX-FileCopyrightText: 2016 Damien P. George
# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
# SPDX-FileCopyrightText: 2019 Roy Hooper
# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: MIT

"""
`adafruit_neopxl8` - Neopixel strip driver using RP2040's PIO
=============================================================

* Author(s): Damien P. George, Scott Shawcroft, Carter Nelson, Roy Hooper, Jeff Epler
"""

import struct
import adafruit_pioasm
import bitops
import adafruit_pixelbuf
import rp2pio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPxl8.git"


_PROGRAM = """
.program piopixl8
top:
    mov pins, null      ; always-low part (last cycle is the 'pull ifempty' after wrap)
    pull block          ; wait for fresh data
    out y, 32           ; get count of NeoPixel bits

; NeoPixels are 800khz bit streams. We are choosing zeros as <312ns hi, 936 lo>
; and ones as <700 ns hi, 546 ns lo> and a clock of 16*800kHz, so the always-high
; time is 4 cycles, the variable time is 5 cycles, and the always-low time is 7 cycles
bitloop:
    pull ifempty [1]     ; don't start outputting HIGH unless data is available (always-low part)
    mov pins, ~ null [3] ; always-high part
    {}                   ; variable part
    mov pins, null       ; always-low part (last cycle is the 'pull ifempty' after wrap)

    jmp y--, bitloop     ; always-low part

; A minimum delay is required so that the next pixel starts refreshing the front of the strands
    pull block
    out y, 32

wait_reset:
    jmp y--, wait_reset
    jmp top
"""


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
        been autowritten. Note that with NeoPxl8 the show operation takes place
        in the background; when this routine returns, the new pixel data has just
        started to be written but your Python code can continue operating in the
        foreground, updating pixel values or performing other computations.

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
    ):  # pylint: disable=too-many-locals
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

        if num_strands == 1:
            data_len = bpp * n
            pack = ">L"
            osr = False
            loop_count = 8 * data_len
        else:
            data_len = bpp * n * 8 // num_strands
            pack = "<L"
            osr = True
            loop_count = data_len
        padding_count = -data_len % 4

        self._num_strands = num_strands
        self._data = bytearray(8 + data_len + padding_count)
        self._data32 = memoryview(self._data).cast("L")
        self._pixels = memoryview(self._data)[4 : 4 + data_len]
        self._data[:4] = struct.pack(pack, loop_count - 1)
        self._data[-4:] = struct.pack(pack, 3840)

        self._num_strands = num_strands

        if num_strands == 8:
            variable_part = "out pins, 8 [4]      ; variable part"
        elif num_strands == 1:
            variable_part = "out pins, 1 [4]      ; variable part"
        else:
            variable_part = f"""
                out pins, {num_strands} [3]       ; variable part
                out x, {8-num_strands}            ; variable part
            """

        program = _PROGRAM.format(variable_part)
        assembled = adafruit_pioasm.assemble(program)

        self._sm = rp2pio.StateMachine(
            assembled,
            frequency=800_000 * 16,
            first_out_pin=data0,
            out_pin_count=num_strands,
            first_set_pin=data0,
            auto_pull=False,
            out_shift_right=osr,
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
        while self._sm.pending:
            pass
        if self.num_strands == 1:
            self._pixels[:] = buffer
            self._sm.background_write(self._data32, swap=True)
        else:
            bitops.bit_transpose(buffer, self._pixels, self._num_strands)
            self._sm.background_write(self._data32)
