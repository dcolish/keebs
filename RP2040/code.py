# SPDX-FileCopyrightText: Copyright (c) 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
MacroPad display image demo. Displays a bitmap image on the built-in display.
"""
import time
from rainbowio import colorwheel

# https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad
from adafruit_macropad import MacroPad


macropad = MacroPad()
text_lines = macropad.display_text(title="Info")
key_number = -1
last_line = ""
tones = [196, 220, 246, 262, 294, 330, 349, 392, 440, 494, 523, 587]

# https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/3d415057b9afd9a80de27c257fb1c147db2312e1/adafruit_hid/consumer_control_code.py#L13
key_map = {
    0: macropad.ConsumerControlCode.REWIND,
    1: macropad.ConsumerControlCode.PLAY_PAUSE,
    2: macropad.ConsumerControlCode.FAST_FORWARD,
}

rot_pos = 0
def get_volume_event(rp):
    global rot_pos
    if rot_pos > rp:
        rot_pos = rp
        return macropad.ConsumerControlCode.VOLUME_DECREMENT
    if rot_pos < rp:
        rot_pos = rp
        return macropad.ConsumerControlCode.VOLUME_INCREMENT

def play_tone():
    macropad.pixels[key_event.key_number] = colorwheel(
        int(255 / 12) * key_event.key_number
    )
    macropad.start_tone(tones[key_event.key_number])

def stop_tone():
    macropad.pixels.fill((0, 0, 0))
    macropad.stop_tone()

while True:
    key_event = macropad.keys.events.get()
    if key_event:
        if key_event.pressed:
            ev = key_map.get(key_event.key_number, ())
            if ev:
                macropad.consumer_control.send(ev)
            key_number = key_event.key_number
            play_tone()
        else:
            stop_tone()
    
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        macropad.consumer_control.send(macropad.ConsumerControlCode.MUTE)

    if rot_pos != macropad.encoder:
        macropad.consumer_control.send(get_volume_event(macropad.encoder))

    last_line = "K:{}\nR:{}\nB:{}".format(key_number, macropad.encoder, macropad.encoder_switch)
    if last_line != text_lines[0].text:
        text_lines[0].text = last_line
        text_lines.show()


