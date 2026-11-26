# Electronics – KiCad (checklist item 4)

KiCad 9 project in the `kicad/` folder: open `ventbox.kicad_pro` with KiCad 9.0 or later.

## Architecture

- **XIAO nRF52840 (U1):** reads the SHT40 (U2) over I2C on pins D4/D5, reads button SW1 on pin D1, switches fan M1 via pin D2, and drives RGB LED D2 (freshness timer) via pins D7/D8/D6.
- **16 × 16 mm sub-board:** connected to the blocks above with soldered wires, contains:
  - Q1 AO3400A, low-side switch for the fan;
  - R1 100 Ω in series with the Q1 gate, R2 10 kΩ gate pull-down to GND so the fan stays off while the XIAO boots;
  - D1 B5819W, fan flyback clamp;
  - button SW1;
  - common-anode RGB LED D2 XINGLIGHT XL-1615RGBC-RF (1.6 × 1.5 × 0.6 mm) with R3 330 Ω (red), R4 150 Ω (green), R5 150 Ω (blue), size 0402;
  - 9 wire solder pads (6 pads of 1.5 mm for power/fan/button, 3 pads of 1.0 mm for the LED).
- **Power:** the fan is powered directly from the battery (VBAT). The XIAO charges the battery from the USB-C port at 50 mA.

| Net | Connects |
|---|---|
| VBAT | BT1+, XIAO BAT+, TP4 (B+), TP5 (F+) → fan red wire, D1 cathode, D2 common anode (pin 2) |
| GND | BT1−, XIAO BAT− and GND, SHT40 GND, Q1 S, R2, SW1, TP3 (G) |
| FAN_PWM | XIAO D2 → TP2 (PW) → R1 |
| GATE | R1 → Q1 G, R2 |
| FAN_SW | Q1 D → TP6 (F−) → fan black wire, D1 anode |
| BTN | XIAO D1 → TP1 (BT) → SW1 |
| LED_R / LED_G / LED_B | XIAO D7 / D8 / D6 → TP7 / TP8 / TP9 → R3 / R4 / R5 → D2 pin 1 / 3 / 4 |
| +3V3, SDA, SCL | XIAO 3V3 / D4 / D5 → SHT40 VCC / SDA / SCL (direct wires) |

The pad labels (BT, PW, G, B+, F+, F−, R, G, B) are printed on the back of the board, directly behind each pad. The back silkscreen also carries "VENTBOX v1.2", "CERN-OHL-S" and "2026-11".

### Timer LED (rev 1.1)

- **Why a common anode tied to VBAT:** the LED lights when the GPIO pin is LOW. When the GPIO is HIGH (3.3 V), the voltage across the LED is only VBAT − 3.3 ≤ 0.9 V, lower than the minimum Vf of the red channel (1.8 V per the [XINGLIGHT datasheet](https://datasheet.lcsc.com/datasheet/pdf/0158170cd0ba772dd3d9a22a67a63b28.pdf?productCode=C965840)), so the LED is fully off.
- **LED current:** about 5–6 mA per channel at VBAT 3.8 V (limit 20 mA). The LED only flashes for 40 ms every 4 s, adding about 0.05 mA average current.
- **Custom footprint:** `kicad/ventbox.pretty/LED_RGB_XINGLIGHT_XL-1615RGBC.kicad_mod`, based on the land pattern on page 8 of the datasheet (pads 0.45 × 0.65; pin 1 R, 2 anode, 3 G, 4 B). The symbol is KiCad's built-in `Device:LED_RAGB`, with the same pin order.
- **Position:** D2 centre at (11.2, 10.0) on the sub-board, aligned with the light pipe VB-07.

## Files

| File | Content |
|---|---|
| `kicad/ventbox.kicad_sch` | Schematic (PDF version: `kicad/ventbox_schematic.pdf`) |
| `kicad/ventbox.kicad_pcb` | PCB 16 × 16 mm, 2 layers, FR-4 0.8 mm, GND copper zone on the top layer |
| `kicad/ventbox.net` | Netlist |
| `kicad/ventbox.kicad_sym`, `sym-lib-table` | Custom symbols: XIAO nRF52840, SHT40 breakout |
| `kicad/ventbox.pretty/`, `fp-lib-table` | Custom footprint: RGB LED XL-1615RGBC-RF |
| `kicad/erc.rpt`, `kicad/drc.rpt` | Check reports |
| `kicad/fab/gerber/` | Gerbers + Excellon drill files; zip them to order from JLCPCB |
| `kicad/fab/ventbox_pos.csv` | Component positions (pick & place) |
| `kicad/fab/ventbox_bom_kicad.csv` | BOM exported from KiCad |
| `kicad/fab/ventbox_pcb.step`, `ventbox_pcb_layers.pdf`, `renders/` | PCB STEP, PDF of each layer, 3D images of top/bottom side |

Check results (KiCad 9.0.8, 08 Nov 2026):
- **ERC:** 0 errors, 0 warnings.
- **DRC (with schematic parity check):** 0 errors, 0 unconnected pads, 0 parity issues.
  - 17 `lib_footprint_mismatch` warnings remain, caused by intentionally moving footprint silkscreen to the F.Fab layer because the board is so small.
- **Design rules:** track 0.3 mm, clearance 0.15 mm, via 0.6/0.3 mm, board-edge clearance 0.3 mm.

## Regenerating from the scripts

Requires KiCad 9 (`kicad-cli` and the bundled Python `pcbnew` module), Java 17 or later and [Freerouting 2.5.0](https://github.com/freerouting/freerouting/releases).

```bash
cd electronics/kicad
python3 ../tools/gen_schematic.py .                                       # schematic + library + _sch_meta.json
kicad-cli sch erc --severity-all -o erc.rpt ventbox.kicad_sch
kicad-cli sch export netlist -o ventbox.net ventbox.kicad_sch
/usr/bin/python3 ../tools/gen_pcb.py . freerouting-2.5.0.jar             # placement + autorouting
/usr/bin/python3 ../tools/fill_zones.py ventbox.kicad_pcb                 # GND copper pour
kicad-cli pcb drc --schematic-parity --severity-all -o drc.rpt ventbox.kicad_pcb
kicad-cli pcb export gerbers -l F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts -o fab/gerber/ ventbox.kicad_pcb
kicad-cli pcb export drill -o fab/gerber/ --excellon-separate-th ventbox.kicad_pcb
kicad-cli pcb export pos --format csv --units mm --side both -o fab/ventbox_pos.csv ventbox.kicad_pcb
kicad-cli sch export pdf -o ventbox_schematic.pdf ventbox.kicad_sch
/usr/bin/python3 ../tools/dump_pcb_parts.py ventbox.kicad_pcb ../../mechanical/cad_native/pcb_parts.json
```

## Ordering the PCB

Zip the `fab/gerber/` folder and upload it to JLCPCB with these parameters:
- 2 layers, FR-4, 0.8 mm thick;
- size 16 × 16 mm, minimum track width and spacing 0.15 mm.

The SMD parts are 0603, 0402, SOT-23 and a 1615 LED.
- 0603 and SOT-23 can be hand-soldered.
- The 1615 LED and the 0402 resistors are very small: use solder paste + hot air, or order JLCPCB's assembly service (PCBA) with `fab/ventbox_pos.csv`.
