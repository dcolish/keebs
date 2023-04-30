import os
import random
import time

# https://github.com/adafruit/Adafruit_CircuitPython_Logging
import adafruit_logging as logging

# https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad
from adafruit_macropad import MacroPad
from rainbowio import colorwheel


VERBOSE_1 = 9

logger = logging.getLogger(__name__)
# [LEVELS](https://github.com/adafruit/Adafruit_CircuitPython_Logging/blob/5.2.1/adafruit_logging.py#L103)
logger.setLevel(logging.DEBUG) # type: ignore - global namespace fiddling occurs...


NUM_KEYS = 12
# pattern is a list of tuples (k, rv)
# TODO: think about row/col level ops
#
# Row 1 - 0, 1, 2
# Row 2 - 3, 4, 5
# Row 3 - 6, 7, 8
# Row 4 - 9, 10, 11
ROWS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)]
COLUMNS = [x for x in zip(*ROWS)]

DEFAULT_FRAME_RATE = 200
KEY_TONES = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]


# TODO: setup stateful keys, actions can be toggled
class Key:
    def on_down(self):
        raise NotImplementedError("Key.on_down unimplemented")

    def on_up(self):
        raise NotImplementedError("Key.on_up unimplemented")


class PixelGrid:
    def __init__(self, macropad) -> None:
        self.macropad = macropad

    def set_pixel_grid(self, pattern):
        for key, color in pattern:
            self.set_pixel(key, color)

    def set_column_color(self, column, color):
        assert 0 <= column <= 2, "column must be 0:2, column:%d" % column
        self.set_pixel_grid(zip(COLUMNS[column], [color] * len(COLUMNS[column])))

    def t_pixel_pattern(self):
        color = 127
        pixels = [0, 1, 2, 4, 7, 10]
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
            (11, color),
        ]
        self.set_pixel_grid(pattern)

    def set_pixel(self, key, color):
        assert 0 <= key <= 11, "key must be between 0:11"
        assert 0 <= color <= 255, "color must be between 0:255, rv:%d" % color
        logger.log(VERBOSE_1, "k:%d" % key)
        logger.log(VERBOSE_1, "rv:%d" % color)
        self.macropad.pixels[key] = colorwheel(color)

    def clear_pixels(self):
        self.macropad.pixels.fill((0, 0, 0))


class Animator:
    def __init__(self, pixel_grid, frames) -> None:
        self.pixel_grid = pixel_grid
        self.frames = frames
        self.next_frame = 0
        self.rate = DEFAULT_FRAME_RATE

    def render(self, step_counter):
        logger.log(VERBOSE_1, "Counter: %d", step_counter)
        if (step_counter % self.rate) == 0:
            self.pixel_grid.clear_pixels()
            logger.debug("frame: %s", self.next_frame)
            # Activate the next frame
            self.frames[self.next_frame % len(self.frames)]()
            self.next_frame += 1


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

    key_number = -1
    last_line = ""
    rot_pos = 0
    key_event = None
    show_rainbow = False
    show_t2_animation = False
    show_columns = False

    def __init__(self) -> None:
        self.macropad = MacroPad()
        self.mcs = self.macropad.consumer_control.send
        self.text_lines = self.macropad.display_text(title="Info")
        self.pixel_grid = PixelGrid(self.macropad)

        self.t2_animator = Animator(
            self.pixel_grid,
            [self.pixel_grid.t_pixel_pattern, self.pixel_grid.number_2_pixel_pattern],
        )

        self.key_map = {
            0: self.rewind,
            1: self.play_pause,
            2: self.fast_forward,
            9: self.toggle_column_display,
            10: self.toggle_t2_animation,
            11: self.toggle_rainbow_display,
        }

    def get_volume_event(self, old_rp, new_rp):
        if old_rp > new_rp:
            return new_rp, self.macropad.ConsumerControlCode.VOLUME_DECREMENT
        if old_rp < new_rp:
            return new_rp, self.macropad.ConsumerControlCode.VOLUME_INCREMENT
        return old_rp, ()

    def play_tone(self, key_number):
        logger.debug("playing tone")
        self.macropad.start_tone(KEY_TONES[key_number])

    def stop_tone(self):
        logger.debug("stopping tone")
        self.macropad.stop_tone()

    def toggle_t2_animation(self):
        logger.debug("toggle t2 pattern display")
        self.show_t2_animation = not self.show_t2_animation

    def toggle_rainbow_display(self):
        logger.debug("toggle rainbow")
        self.show_rainbow = not self.show_rainbow

    def toggle_column_display(self):
        logger.debug("toggle column")
        self.show_columns = not self.show_columns

    def rewind(self):
        logger.debug("rewind")
        self.mcs(self.macropad.ConsumerControlCode.REWIND)

    def play_pause(self):
        logger.debug("play pause")
        self.mcs(self.macropad.ConsumerControlCode.PLAY_PAUSE)

    def fast_forward(self):
        logger.debug("fast forward")
        self.mcs(self.macropad.ConsumerControlCode.FAST_FORWARD)

    def run(self, ctx):
        ctx["counter"] += 1
        self.key_event = self.macropad.keys.events.get()
        if self.key_event:
            if self.key_event.pressed:
                logger.debug("pressed: %d", self.key_event.key_number)
                cb = self.key_map.get(self.key_event.key_number, ())
                if cb:
                    cb()
                self.key_number = self.key_event.key_number
                self.pixel_grid.set_pixel(
                    self.key_number, int(255 / 12) * self.key_number
                )
                if ctx["settings"]["keytones"]:
                    self.play_tone(self.key_number)
            else:
                self.pixel_grid.clear_pixels()
                self.stop_tone()

        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            self.macropad.consumer_control.send(self.macropad.ConsumerControlCode.MUTE)

        self.rot_pos, ev = self.get_volume_event(self.rot_pos, self.macropad.encoder)
        if ev:
            self.macropad.consumer_control.send(ev)

        # TODO: make animations mutally exclusive
        if self.show_rainbow:
            self.pixel_grid.set_pixel(random.randint(0, 11), random.randint(0, 255))

        if self.show_t2_animation:
            self.t2_animator.render(ctx["counter"])

        if self.show_columns:
            self.pixel_grid.set_column_color(0, 40)

        last_line = "K:{}\nR:{}\nB:{}".format(
            self.key_number, self.macropad.encoder, self.macropad.encoder_switch
        )
        if last_line != self.text_lines[0].text:
            self.text_lines[0].text = last_line
            self.text_lines.show()


def main():
    settings = {
        "keytones": bool(os.getenv("keytones", 0)),
        "animation_rate": int(os.getenv("animation_rate", DEFAULT_FRAME_RATE)),
    }
    ctx = {
        "counter": 0,
        "next_frame": 0,
        "settings": settings,
    }
    pad = RadPad()
    while True:
        pad.run(ctx)


main()
