# VENTBOX
Official documentation for the ventbox, maintained by Group 2_ GPE PROJECT (VGU_GPE25). This repository contains a technical description, an assembly guide, a Bill of Materials, as well as STEPs and STLs for the 3D printed parts.

VENTBOX is a smart storage solution that helps reduce food waste by actively controlling humidity inside food containers. Its thin, surface-mounted module can be added to existing Lock &amp; Lock lids without affecting the ability to stack containers in the refrigerator.

Ventbox is a module that mounts on the original lid of a 1.9 L Lock & Lock HPL818 food container (the lid only needs two holes, Ø12.3 and Ø10.3). It extracts moist air from the container to limit condensation while the container is kept in the refrigerator.
The module protrudes 8.0 mm above the lid surface and measures 92.8 × 43.3 × 7.5 mm. It is controlled by a Seeed XIAO nRF52840 with an SHT40 sensor; Sunon UB5U3-700 centrifugal blower fan; LP303035 LiPo battery.
Since rev 1.1 there is also a freshness timer: hold the button for 2 s when storing food, and the RGB LED on the module cover flashes green for 2 days, orange for 3 days, red for 2 days, then red double flashes once 7 days have passed. The timer runs independently of the fan and shares the XIAO, battery and button (firmware/README.md).


License

The license "CERN Open Hardware Licence Version 2 - Strongly Reciprocal" applies to all parts of the documentation in the repository.

Disclaimer

For Experienced Users Only
 This project is intended for individuals with sufficient knowledge and experience in handling electrical devices, components, and tools. Users are responsible for ensuring that any construction, modification, or operation is carried out safely and in accordance with applicable laws and regulations.

No Safety Guarantee
 The information provided is based on publicly available resources and is intended for educational and experimental purposes only. A self-built container/box does not replace a commercially manufactured and certified appliance. No representation, warranty, or guarantee is made regarding the safety, reliability, performance, or suitability of any device constructed using this information.

Use at Your Own Risk
 Any construction, modification, or use of a self-built container/box is undertaken entirely at your own risk. The author and contributors accept no responsibility or liability for any damage, injury, loss, malfunction, or other consequences resulting from the use of the information provided.

Not a Certified Product
 Any container/box built using this documentation is not a CE-certified product and has not been tested or approved under the standards applicable to commercial kitchen appliances or consumer products.

Prototype Status
 The self-built container/box should be considered a prototype or experimental device. It may not meet the safety, electrical, mechanical, food-contact, or regulatory requirements applicable to commercial products. Users are strongly advised to exercise caution and provide appropriate supervision during testing and operation.

Independent of Commercial Products
 This documentation is provided separately from any commercial products offered by the author and is intended solely for educational purposes. The purchase of any product from the author does not automatically grant rights to, include, or require the use of this documentation. Any use of the documentation is entirely independent of any product purchase.

Acceptance of Terms
 By accessing, using, or relying on the information provided, you acknowledge that you have read, understood, and agreed to this disclaimer. You assume full responsibility for the construction, operation, and use of any self-built container/box and do so entirely at your own risk.
How to start

Use the document "Technical documentation, BOM and Assembly Guide" to familiarise yourself with VENTBOX. The Bill of Materials included in the document contains the component names which are reused throughout the Github project.

Assembly_guide	  9-step illustrated assembly guide (ASSEMBLY\\\_GUIDE.md)
3D Model in step file/            STEP AP214/AP242 assembly + parts/\\\*.step,
DXF/       			 2D drawings dxf
3D-printed components/            STL files of the 3D-printed parts (base, module cover, 2 nuts, button, light pipe)
Electronics/
kicad/           ventbox.kicad_pro / .kicad_sch / .kicad_pcb / .kicad_sym / .net, ERC + DRC
kicad/fab/       gerbers + drill, component positions, PCB STEP, PCB layer PDF, render images
tools/           scripts that generate the schematic and PCB (fully reproducible)
Firmware/
ventbox/         ventbox.ino
build/           compiled .hex and DFU .zip package
Datasheets/        11 PDF datasheets
```

## Verification status (08 Nov 2026)

|Item|Result|
|-|-|
|3D model|Rev 1.1: housing split into module base + module cover, modelled threads, watertight STL; all solids valid, no interference between parts (`chk\\\\\\\\\\\\\\\_addon.py`); the lid only loses 303 mm³, exactly the volume of the 2 holes|
|Schematic|ERC: 0 errors, 0 warnings|
|PCB|Rev 1.2 (rev 1.1 added RGB LED D2, R3–R5, TP7–TP9): DRC 0 errors, 0 unconnected pads; the 17 `lib\\\\\\\\\\\\\\\_footprint\\\\\\\\\\\\\\\_mismatch` warnings are caused by intentionally moving footprint silkscreen to the Fab layer (the 16 × 16 mm board is too small)|
|Firmware|v1.2 (freshness timer since v1.1) compiles successfully for `Seeeduino:nrf52:xiaonRF52840`: 52 660 bytes (6 % flash)|
|Tested on real hardware|Not yet. When a prototype is available, re-measure the XIAO height, check the fan fit, and check the LED brightness and orange colour through the light pipe|

## Third-party software

The firmware `firmware/ventbox/ventbox.ino` is original Group 2 code. It uses these standard open-source libraries (not copied into the repo; installed via the Arduino Library/Boards Manager):

\* Wire (I2C), part of the \[Seeed nRF52 Arduino core](https://github.com/Seeed-Studio/Adafruit\_nRF52\_Arduino) – Arduino LLC / Sandeep Mistry / Adafruit, LGPL-2.1
\* \[Adafruit SHT4x Library](https://github.com/adafruit/Adafruit\_SHT4x) – Adafruit Industries, BSD
\* \[Adafruit BusIO](https://github.com/adafruit/Adafruit\_BusIO) – Adafruit Industries, MIT
\* \[Adafruit Unified Sensor](https://github.com/adafruit/Adafruit\_Sensor) – Adafruit Industries, Apache-2.0
\* \[Seeed nRF52 Boards core 1.1.13](https://github.com/Seeed-Studio/Adafruit\_nRF52\_Arduino) incl. \[Adafruit TinyUSB](https://github.com/adafruit/Adafruit\_TinyUSB\_Arduino) – Seeed Studio / Adafruit, LGPL-2.1 / MIT

Versions, purpose and licence of each library: \[firmware/README.md](firmware/README.md#third-party-libraries-and-origin).

## Licence

Hardware, documentation and firmware are released under the CERN Open Hardware Licence Version 2 – Strongly Reciprocal (CERN-OHL-S v2), the course default (KickOff p. 49 #10). The LICENSE file is added by the person responsible for checklist item 12.

