# RP2040 Macropad

Messing around with circuitpython

## Flashing

[To enter the bootloader, hold down the BOOT/BOOTSEL button (highlighted in red
above), and while continuing to hold it (don't let go!), press and release the
reset button (highlighted in blue above). Continue to hold the BOOT/BOOTSEL
button until the RPI-RP2 drive
appears!](https://learn.adafruit.com/adafruit-macropad-rp2040/circuitpython#:~:text=To%20enter%20the%20bootloader%2C%20hold%20down%20the%20BOOT/BOOTSEL%20button%20(highlighted%20in%20red%20above)%2C%20and%20while%20continuing%20to%20hold%20it%20(don%27t%20let%20go!)%2C%20press%20and%20release%20the%20reset%20button%20(highlighted%20in%20blue%20above).%20Continue%20to%20hold%20the%20BOOT/BOOTSEL%20button%20until%20the%20RPI%2DRP2%20drive%20appears!)

Use [Safe
Mode](https://learn.adafruit.com/adafruit-macropad-rp2040/circuitpython#safe-mode-3097754)
to recover your board.

## Runtime env

See https://learn.adafruit.com/scrolling-countdown-timer/create-your-settings-toml-file

Example

```sh
# Comments are supported
CIRCUITPY_WIFI_SSID="guest wifi"
CIRCUITPY_WIFI_PASSWORD="guessable"
CIRCUITPY_WEB_API_PORT=80
CIRCUITPY_WEB_API_PASSWORD="passw0rd"
test_variable="this is a test"
thumbs_up="\U0001f44d"
```

## Circuit Python

https://docs.circuitpython.org/projects/macropad/en/latest/examples.html

[Macropad API reference](https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad)

[Display](https://docs.circuitpython.org/projects/display_text/en/latest/)
[HID Ref](https://docs.circuitpython.org/projects/hid/en/latest/)

### Interesting folders in the repo

* Adafruit_Learning_System_Guides/Macropad_Hotkeys
  * DSL for defining macros


## Troubleshooting

<https://learn.adafruit.com/adafruit-macropad-rp2040/troubleshooting>
