# SPDX-FileCopyrightText: Copyright (c) 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
MacroPad display image demo. Displays a bitmap image on the built-in display.
"""
import random
import time

# https://github.com/adafruit/Adafruit_CircuitPython_Logging
import adafruit_logging as logging
# https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad
from adafruit_macropad import MacroPad
from rainbowio import colorwheel

# TODO use `settings.toml`

logger = logging.getLogger(__name__)
# [LEVELS](https://github.com/adafruit/Adafruit_CircuitPython_Logging/blob/5.2.1/adafruit_logging.py#L103)
logger.setLevel(logging.DEBUG)
VERBOSE_1 = 9

NUM_KEYS = 12
ROWS = [
    (0,1,2),
    (3,4,5),
    (6,7,8),
    (9,10,11)
]
COLUMNS = zip(*ROWS)
ANIMATION_RATE=200

class RadPad:
    """Wrapper for adafruit_macropad

    Functions
        * [ConsumerControlCodes](https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/3d415057b9afd9a80de27c257fb1c147db2312e1/adafruit_hid/consumer_control_code.py#L13)
            * Key 0 - Rewind
            * Key 1 - Play Pause
            * Key 2 - Fast Forward
            * Encoder Rotation - CW:Volume Up, CCW:Volume Down
            * Encoder Button - Mute
    """
    key_tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]
    key_number = -1
    last_line = ""
    rot_pos = 0
    key_event = None
    show_rainbow = False
    show_t2 = False


    def __init__(self) -> None:
        self.macropad = MacroPad()
        self.mcs = self.macropad.consumer_control.send
        self.text_lines = self.macropad.display_text(title="Info")
        self.key_map = {
            0: self.rewind,
            1: self.play_pause,
            2: self.fast_forward,
            10: self.toggle_t2_pattern,
            11: self.toggle_rainbow_display,
        }


    def get_volume_event(self, old_rp, new_rp):
        if old_rp > new_rp:
            return new_rp, self.macropad.ConsumerControlCode.VOLUME_DECREMENT
        if old_rp < new_rp:
            return new_rp, self.macropad.ConsumerControlCode.VOLUME_INCREMENT
        return old_rp, ()

    def play_tone(self):
        logger.debug("playing tone")
        self.set_pixel(self.key_event.key_number, int(255 / 12) * self.key_event.key_number)
        self.macropad.start_tone(self.key_tones[self.key_event.key_number])


    def stop_tone(self):
        logger.debug("stopping tone")
        self.macropad.stop_tone()


    def set_pixel(self, key, color):
        assert 0 <= key <= 11, "key must be between 0:11"
        assert 0 <= color <= 255, "color must be between 0:255, rv:%d" % color
        logger.log(VERBOSE_1, "k:%d" % key)
        logger.log(VERBOSE_1, "rv:%d" % color)
        self.macropad.pixels[key] = colorwheel(color)

    def toggle_t2_pattern(self):
        logger.debug("toggle t2 pattern display")
        self.show_t2 = not self.show_t2

    # pattern is a list of tuples (k, rv)
    # TODO: think about row/col level ops
    #
    # Row 1 - 0, 1, 2
    # Row 2 - 3, 4, 5
    # Row 3 - 6, 7, 8
    # Row 4 - 9, 10, 11
    #
    # 
    def set_pixel_grid(self, pattern):
        for key, color in pattern:
            self.set_pixel(key, color)


    def t_pixel_pattern(self):
        color = 127
        pixels = [0,1,2,4,7,10]
        pattern = zip(pixels, [color] * len(pixels))
        self.set_pixel_grid(pattern)


    def number_2_pixel_pattern(self):
        color = 127
        pattern = [
            (0, color),
            (1, color),
            (2, color),
            (5, color),
            (7, color),
            (9, color),
            (10, color),
            (11, color)
        ]
        self.set_pixel_grid(pattern)

    def clear_pixels(self):
        self.macropad.pixels.fill((0, 0, 0))

    def toggle_rainbow_display(self):
        logger.debug("toggle rainbow")
        self.show_rainbow = not self.show_rainbow


    def rewind(self):
        logger.debug("rewind")
        self.mcs(self.macropad.ConsumerControlCode.REWIND)


    def play_pause(self):
        logger.debug("play pause")
        self.mcs(self.macropad.ConsumerControlCode.PLAY_PAUSE)


    def fast_forward(self):
        logger.debug("fast forward")
        self.mcs(self.macropad.ConsumerControlCode.FAST_FORWARD)

    def animate(self, ctx, frames, rate):
        logger.log(VERBOSE_1, "Counter: %d", ctx["counter"])
        if (ctx["counter"] % rate) == 0:
            self.clear_pixels()
            logger.debug("frame: %s", ctx["next_frame"])
            # Activate the next frame
            frames[ctx["next_frame"] % len(frames)]()
            ctx["next_frame"] += 1


    def run(self, ctx):
        ctx['counter'] += 1
        self.key_event = self.macropad.keys.events.get()
        if self.key_event:
            if self.key_event.pressed:
                logger.debug("pressed: %d", self.key_event.key_number)
                cb = self.key_map.get(self.key_event.key_number, ())
                if cb:
                    cb()
                self.key_number = self.key_event.key_number
                self.play_tone()
            else:
                self.clear_pixels()
                self.stop_tone()
        
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            self.macropad.consumer_control.send(self.macropad.ConsumerControlCode.MUTE)

        self.rot_pos, ev = self.get_volume_event(self.rot_pos, self.macropad.encoder)
        if ev:
            self.macropad.consumer_control.send(ev)

        if self.show_rainbow:
            self.set_pixel(random.randint(0,11), random.randint(0,255))

        if self.show_t2:
            # TODO: make rate configuration only
            self.animate(
                ctx, [self.t_pixel_pattern, self.number_2_pixel_pattern], ANIMATION_RATE)

        last_line = "K:{}\nR:{}\nB:{}".format(
            self.key_number, self.macropad.encoder, self.macropad.encoder_switch)
        if last_line != self.text_lines[0].text:
            self.text_lines[0].text = last_line
            self.text_lines.show()

pad = RadPad()
ctx = {
        "counter": 0,
        "next_frame": 0,
    }
while True:
    pad.run(ctx)