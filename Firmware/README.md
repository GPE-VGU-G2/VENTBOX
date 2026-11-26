# Firmware (checklist item 4)

`ventbox/ventbox.ino` – Arduino, runs on the Seeed XIAO nRF52840.

## Operation (v1.2)

The firmware has 2 functions that run independently and only share the XIAO, the battery and button SW1. v1.2 is the English release (comments and documentation translated); its behaviour is identical to v1.1.

### Humidity extraction

- **Periodic measurement:** the SHT40 measures the humidity every 60 s.
- **Automatic fan run:** when RH ≥ 85 %, the fan runs for 30 s, pauses and measures again, repeating until RH ≤ 75 %.
- **Short press (< 0.8 s):** runs a 120 s quick purge, used right after storing food that is still warm. Short press again to stop.
- **Battery protection:** below 3.35 V the fan does not run; the LED flashes blue/red alternately 3 times (different from the red of the timer).
- **Fan control:** the fan is only switched on/off, not PWM-controlled, because the Sunon datasheet requires a constant voltage.
- **Battery charging:** 50 mA charge current (pin P0.13 left floating).
- **Pin P0.14 (VBAT_ENABLE):** always held LOW, following the [Seeed Wiki](https://wiki.seeedstudio.com/XIAO_BLE/) warning about possible damage to pin P0.31 while charging.

### Freshness timer (RGB LED D2)

![LED freshness timer](../docs/assembly_guide/img/LED_freshness_timer_7_days.png)

| Action | Result |
|---|---|
| Hold the button 2 s, release when it flashes green | Start / reset the 7-day timer; the LED flashes green 3 times |
| Hold the button 5 s, release when it flashes red | Switch the timer off; the LED flashes blue 2 times |
| Short press | In addition to the quick purge, the LED immediately shows the current timer colour |

| Time since set | LED (40 ms flash every 4 s) | Meaning |
|---|---|---|
| 0 – 2 days | green | fresh |
| 2 – 5 days | orange (red + 14 % green) | use soon |
| 5 – 7 days | red | stored for a long time |
| after 7 days | red double flash | expired |
| not set / switched off | off | |

Technical details:
- **Time keeping:** accumulated from `millis()` (32.768 kHz crystal clock) into a 64-bit variable, so it does not overflow after 49 days.
- **Power loss:** a flat battery or re-flashing the firmware clears the timer. At start-up the LED flashes red, green, blue once as a self-test.
- **Orange colour:** mixed with 1 kHz software PWM during the flash, so it does not depend on the hardware PWM peripheral.
- **On-board XIAO LED:** hidden inside the base, so the firmware switches it off completely and only uses LED D2.

| Constant | Default | Meaning |
|---|---|---|
| `RH_ON` / `RH_OFF` | 85 / 75 %RH | Fan on / off thresholds |
| `CHECK_S` | 60 s | Measurement period |
| `RUN_S` | 30 s | Fan run time per cycle |
| `BURST_S` | 120 s | Quick-purge duration on button press |
| `VBAT_MIN` | 3.35 V | Low-battery threshold |
| `GREEN_H` / `ORANGE_H` / `RED_H` | 48 / 72 / 48 hours | Length of the green / orange / red phases (7 days in total) |
| `BLINK_S`, `FLASH_MS` | 4 s, 40 ms | Flash period and flash length |
| `HOLD_SET_MS` / `HOLD_OFF_MS` | 2000 / 5000 ms | Button hold time to set / switch off the timer |
| `C_GREEN`, `C_ORANGE`, ... | % brightness per channel | Tune the orange colour on the real prototype |

## Third-party libraries and origin

`ventbox/ventbox.ino` is original code written by Group 2 for Ventbox (no vendor firmware was downloaded or reused). It only calls the standard libraries below, which are **not copied into this repo**; they are installed by the Arduino IDE / arduino-cli from their official sources and keep their own licences.

| Library / package | Version used | Used for | Author / origin | Source | Licence |
|---|---|---|---|---|---|
| Wire (TWI/I2C for nRF5x) | bundled with core 1.1.13 | I2C bus to the SHT40 | Arduino LLC, Sandeep Mistry, Adafruit; shipped in the Seeed nRF52 core | [Seeed-Studio/Adafruit_nRF52_Arduino – libraries/Wire](https://github.com/Seeed-Studio/Adafruit_nRF52_Arduino/tree/master/libraries/Wire), [Arduino Wire reference](https://docs.arduino.cc/language-reference/en/functions/communication/wire/) | LGPL-2.1 |
| Adafruit SHT4x Library | 1.0.5 | Read temperature / humidity from the SHT40 | Adafruit Industries | [github.com/adafruit/Adafruit_SHT4x](https://github.com/adafruit/Adafruit_SHT4x) | BSD |
| Adafruit BusIO (dependency) | 1.17.4 | I2C helper used by the SHT4x library | Adafruit Industries | [github.com/adafruit/Adafruit_BusIO](https://github.com/adafruit/Adafruit_BusIO) | MIT |
| Adafruit Unified Sensor (dependency) | 1.1.15 | Common sensor interface used by the SHT4x library | Adafruit Industries | [github.com/adafruit/Adafruit_Sensor](https://github.com/adafruit/Adafruit_Sensor) | Apache-2.0 |
| Seeed nRF52 Boards (Arduino core, board support) | 1.1.13 | Arduino core, `millis()`, GPIO, ADC, bootloader upload for XIAO nRF52840 | Seeed Studio, fork of the Adafruit nRF52 core | [github.com/Seeed-Studio/Adafruit_nRF52_Arduino](https://github.com/Seeed-Studio/Adafruit_nRF52_Arduino), board index `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`, [Seeed Wiki – XIAO nRF52840](https://wiki.seeedstudio.com/XIAO_BLE/) | LGPL-2.1 |
| Adafruit TinyUSB (bundled with the core) | 1.7.0 | USB serial / upload | Ha Thach for Adafruit Industries | [github.com/adafruit/Adafruit_TinyUSB_Arduino](https://github.com/adafruit/Adafruit_TinyUSB_Arduino) | MIT |
| adafruit-nrfutil (tool, not linked into the firmware) | latest from PyPI | Packs the `.zip` and uploads over USB | Adafruit Industries | [github.com/adafruit/Adafruit_nRF52_nrfutil](https://github.com/adafruit/Adafruit_nRF52_nrfutil) | BSD-3-Clause |
| arduino-cli (build tool) | 1.5.1 | Command-line compile / upload | Arduino SA | [github.com/arduino/arduino-cli](https://github.com/arduino/arduino-cli) | GPL-3.0 |

The compiled `build/ventbox.ino.hex` / `.zip` contain linked code from the Wire, SHT4x, BusIO, Unified Sensor, core and TinyUSB libraries; their licence texts are available at the links above.

## Building with the Arduino IDE

1. Go to File > Preferences > Additional Boards Manager URLs and add `https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json`.
2. Open the Boards Manager and install Seeed nRF52 Boards (the version without "mbed"), version 1.1.13.
3. Open the Library Manager and install Adafruit SHT4x Library. It automatically pulls in Adafruit BusIO and Adafruit Unified Sensor.
4. Select Board Seeed XIAO nRF52840 and Port XIAO nRF52840, then click Upload. If the upload fails, double-press the reset button quickly to enter the bootloader.

## Building from the command line (verified)

```bash
arduino-cli config add board_manager.additional_urls https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json
arduino-cli core update-index
arduino-cli core install Seeeduino:nrf52@1.1.13
arduino-cli lib install "Adafruit SHT4x Library"
pip install adafruit-nrfutil
cd firmware
arduino-cli compile -b Seeeduino:nrf52:xiaonRF52840 --output-dir build ventbox
arduino-cli upload  -b Seeeduino:nrf52:xiaonRF52840 -p /dev/ttyACM0 ventbox
```

Environment of the successful build on 08 Nov 2026:
- arduino-cli 1.5.1, Seeeduino:nrf52 1.1.13;
- Adafruit SHT4x 1.0.5, Adafruit BusIO 1.17.4, Adafruit Unified Sensor 1.1.15, Adafruit TinyUSB 1.7.0 (bundled with the core).

Result v1.2: 52 660 bytes flash (6 %), 7 740 bytes RAM (3 %).

`build/ventbox.ino.hex` and `build/ventbox.ino.zip` (DFU package for adafruit-nrfutil) are the precompiled binaries. Not yet tested on real hardware.
