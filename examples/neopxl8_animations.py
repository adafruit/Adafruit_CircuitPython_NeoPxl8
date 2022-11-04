# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: Unlicense

# Set up a separate animation on each of 8 strips with NeoPxl8

import board
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.helper import PixelMap
from adafruit_led_animation import color
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
    auto_write=False,
    brightness=0.07,
)


def strand(i):
    return PixelMap(
        pixels,
        range(i * strand_length, (i + 1) * strand_length),
        individual_pixels=True,
    )


strands = [strand(i) for i in range(num_strands)]

animations = AnimationGroup(
    Comet(strands[0], 0.5, color.CYAN),
    Comet(strands[1], 0.4, color.AMBER),
    RainbowComet(strands[2], 0.3),
    RainbowComet(strands[3], 0.7),
    Chase(strands[4], 0.05, size=2, spacing=3, color=color.PURPLE),
    RainbowChase(strands[5], 0.05, size=2, spacing=3),
    Rainbow(strands[6], 0.6),
    Rainbow(strands[7], 0.23, step=21),
)

while True:
    animations.animate()
