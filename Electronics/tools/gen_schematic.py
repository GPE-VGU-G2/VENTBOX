"""Generate the KiCad 9 schematic (.kicad_sch) + project symbol library for the Ventbox module.
Run: python3 gen_schematic.py <project_dir>
Connections use net labels placed at the end of a short wire stub from each pin -> easy to read, ERC-checkable.
"""
import sys, os, uuid, re, json

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
PROJ = "ventbox"
KLIB = "/usr/share/kicad/symbols/"
U = lambda: str(uuid.uuid4())
ROOT = U()

# ---------- read symbols from the standard library ----------
def extract(libfile, name):
    txt = open(KLIB + libfile).read()
    i = txt.index('\n\t(symbol "%s"' % name) + 1
    d, j = 0, i
    while True:
        c = txt[j]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        elif c == '"':
            j += 1
            while txt[j] != '"':
                if txt[j] == '\\': j += 1
                j += 1
        j += 1
    return txt[i:j + 1]

def pins_of(block):
    pins = {}
    for m in re.finditer(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length [-\d.]+\)(?:\s*hide)?\s*\(name "([^"]*)"[\s\S]*?\(number "([^"]+)"', block):
        pins[m.group(6)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))
    return pins

STD = {"Device:R": ("Device.kicad_sym", "R"), "Device:D_Schottky": ("Device.kicad_sym", "D_Schottky"),
       "Device:Battery_Cell": ("Device.kicad_sym", "Battery_Cell"),
       "Transistor_FET:Q_NMOS_GSD": ("Transistor_FET.kicad_sym", "Q_NMOS_GSD"),
       "Switch:SW_Push": ("Switch.kicad_sym", "SW_Push"), "Motor:Fan": ("Motor.kicad_sym", "Fan"),
       "Connector:TestPoint": ("Connector.kicad_sym", "TestPoint"),
       "Device:LED_RAGB": ("Device.kicad_sym", "LED_RAGB")}

# ---------- project-specific symbols ----------
def custom_symbol(name, ref, value, fp, ds, left, right, w=12.7, desc=""):
    """left/right: list (number, name). Pin length 2.54, pitch 2.54."""
    n = max(len(left), len(right))
    h = (n + 1) * 2.54
    top = h / 2
    s = [f'\t(symbol "{name}"', '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)']
    def prop(k, v, y, hide=False):
        return (f'\t\t(property "{k}" "{v}"\n\t\t\t(at 0 {y:.2f} 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)'
                + ('\n\t\t\t\t(hide yes)' if hide else '') + '\n\t\t\t)\n\t\t)')
    s += [prop("Reference", ref, top + 1.27), prop("Value", value, -top - 1.27), prop("Footprint", fp, -top - 3.81, True),
          prop("Datasheet", ds, -top - 6.35, True), prop("Description", desc, -top - 8.89, True)]
    s.append(f'\t\t(symbol "{name.split(":")[-1]}_0_1"\n\t\t\t(rectangle\n\t\t\t\t(start {-w/2:.2f} {top:.2f})\n\t\t\t\t(end {w/2:.2f} {-top:.2f})'
             '\n\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n\t\t\t\t(fill\n\t\t\t\t\t(type background)\n\t\t\t\t)\n\t\t\t)\n\t\t)')
    s.append(f'\t\t(symbol "{name.split(":")[-1]}_1_1"')
    for side, lst in ((0, left), (1, right)):
        for k, (num, nm, typ) in enumerate(lst):
            y = top - 2.54 * (k + 1)
            x = -w/2 - 2.54 if side == 0 else w/2 + 2.54
            ang = 0 if side == 0 else 180
            s.append(f'\t\t\t(pin {typ} line\n\t\t\t\t(at {x:.2f} {y:.2f} {ang})\n\t\t\t\t(length 2.54)\n\t\t\t\t(name "{nm}"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)'
                     f'\n\t\t\t\t(number "{num}"\n\t\t\t\t\t(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)')
    s.append('\t\t)\n\t\t(embedded_fonts no)\n\t)')
    return "\n".join(s)

B = "bidirectional"; P = "passive"
XIAO_L = [("1", "D0/A0", B), ("2", "D1/A1", B), ("3", "D2/A2", B), ("4", "D3/A3", B), ("5", "D4/SDA", B), ("6", "D5/SCL", B), ("7", "D6/TX", B), ("15", "BAT+", P)]
XIAO_R = [("14", "5V", P), ("13", "GND", P), ("12", "3V3", P), ("11", "D10/MOSI", B), ("10", "D9/MISO", B), ("9", "D8/SCK", B), ("8", "D7/RX", B), ("16", "BAT-", P)]
SHT_L = [("1", "VCC", P), ("2", "GND", P), ("3", "SCL", B), ("4", "SDA", B)]
CUSTOM = {
    f"{PROJ}:XIAO_nRF52840": custom_symbol(f"{PROJ}:XIAO_nRF52840", "U", "XIAO_nRF52840", "", "https://wiki.seeedstudio.com/XIAO_BLE/",
                                          XIAO_L, XIAO_R, 27.94, "Seeed Studio XIAO nRF52840, module 21x17.8 mm, on-board LiPo charger (BQ25101)"),
    f"{PROJ}:SHT40_Breakout": custom_symbol(f"{PROJ}:SHT40_Breakout", "U", "SHT40_7Semi_ES-13521", "", "https://evelta.com/content/datasheets/7Semi%20_ES-13521_SHT40_BREAKOUT_1.0.pdf",
                                           SHT_L, [], 12.7, "7Semi ES-13521 SHT40 sensor breakout 18.92x6.12 mm, I2C 0x44"),
}

# ---------- part list ----------
# (ref, lib_id, value, footprint, x, y, on_board, extra props)
FP_TP = "TestPoint:TestPoint_Pad_1.5x1.5mm"
FP_TP1 = "TestPoint:TestPoint_Pad_1.0x1.0mm"
PARTS = [
    ("U1", f"{PROJ}:XIAO_nRF52840", "XIAO_nRF52840", "", 80.01, 63.5, False, {"MPN": "102010448", "Supplier": "Seeed Studio"}),
    ("U2", f"{PROJ}:SHT40_Breakout", "SHT40_7Semi_ES-13521", "", 80.01, 124.46, False, {"MPN": "ES-13521", "Supplier": "7Semi"}),
    ("BT1", "Device:Battery_Cell", "LiPo_LP303035_3.7V_310mAh", "", 25.4, 66.04, False, {"MPN": "LP303035", "Supplier": "LiPol Battery"}),
    ("M1", "Motor:Fan", "Sunon_UB5U3-700", "", 182.88, 55.88, False, {"MPN": "UB5U3-700", "Supplier": "Sunon"}),
    ("Q1", "Transistor_FET:Q_NMOS_GSD", "AO3400A", "Package_TO_SOT_SMD:SOT-23", 205.74, 101.6, True, {"MPN": "AO3400A", "LCSC": "C20917"}),
    ("R1", "Device:R", "100", "Resistor_SMD:R_0603_1608Metric", 182.88, 101.6, True, {"MPN": "0603WAF1000T5E", "LCSC": "C22775"}),
    ("R2", "Device:R", "10k", "Resistor_SMD:R_0603_1608Metric", 193.04, 111.76, True, {"MPN": "0603WAF1002T5E", "LCSC": "C25804"}),
    ("D1", "Device:D_Schottky", "B5819W", "Diode_SMD:D_SOD-123", 208.28, 55.88, True, {"MPN": "B5819W SL", "LCSC": "C8598"}),
    ("SW1", "Switch:SW_Push", "TS-1187A", "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", 149.86, 132.08, True, {"MPN": "TS-1187A-B-A-B", "LCSC": "C318884"}),
    ("TP1", "Connector:TestPoint", "BTN", FP_TP, 132.08, 149.86, True, {}),
    ("TP2", "Connector:TestPoint", "PWM", FP_TP, 152.4, 149.86, True, {}),
    ("TP3", "Connector:TestPoint", "GND", FP_TP, 172.72, 149.86, True, {}),
    ("TP4", "Connector:TestPoint", "VBAT", FP_TP, 193.04, 149.86, True, {}),
    ("TP5", "Connector:TestPoint", "FAN+", FP_TP, 213.36, 149.86, True, {}),
    ("TP6", "Connector:TestPoint", "FAN-", FP_TP, 233.68, 149.86, True, {}),
    # rev 1.1: RGB LED for the freshness timer green / orange / red
    ("D2", "Device:LED_RAGB", "XL-1615RGBC-RF", "ventbox:LED_RGB_XINGLIGHT_XL-1615RGBC", 152.4, 63.5, True, {"MPN": "XL-1615RGBC-RF", "LCSC": "C965840"}),
    ("R3", "Device:R", "330", "Resistor_SMD:R_0402_1005Metric", 119.38, 63.5, True, {"MPN": "0402WGF3300TCE", "LCSC": "C25104"}),
    ("R4", "Device:R", "150", "Resistor_SMD:R_0402_1005Metric", 127.0, 63.5, True, {"MPN": "0402WGF1500TCE", "LCSC": "C25082"}),
    ("R5", "Device:R", "150", "Resistor_SMD:R_0402_1005Metric", 134.62, 63.5, True, {"MPN": "0402WGF1500TCE", "LCSC": "C25082"}),
    ("TP7", "Connector:TestPoint", "LED_R", FP_TP1, 132.08, 167.64, True, {}),
    ("TP8", "Connector:TestPoint", "LED_G", FP_TP1, 152.4, 167.64, True, {}),
    ("TP9", "Connector:TestPoint", "LED_B", FP_TP1, 172.72, 167.64, True, {}),
]
# net: list (ref, pin)
NETS = {
    "VBAT": [("BT1", "1"), ("U1", "15"), ("TP4", "1"), ("TP5", "1"), ("M1", "1"), ("D1", "1"), ("D2", "2")],
    "GND": [("BT1", "2"), ("U1", "16"), ("U1", "13"), ("U2", "2"), ("Q1", "2"), ("R2", "2"), ("SW1", "2"), ("TP3", "1")],
    "+3V3": [("U1", "12"), ("U2", "1")],
    "SDA": [("U1", "5"), ("U2", "4")],
    "SCL": [("U1", "6"), ("U2", "3")],
    "FAN_PWM": [("U1", "3"), ("TP2", "1"), ("R1", "1")],
    "GATE": [("R1", "2"), ("Q1", "1"), ("R2", "1")],
    "FAN_SW": [("Q1", "3"), ("M1", "2"), ("D1", "2"), ("TP6", "1")],
    "BTN": [("U1", "2"), ("TP1", "1"), ("SW1", "1")],
    "LED_R": [("U1", "8"), ("TP7", "1"), ("R3", "1")],
    "LED_RK": [("R3", "2"), ("D2", "1")],
    "LED_G": [("U1", "9"), ("TP8", "1"), ("R4", "1")],
    "LED_GK": [("R4", "2"), ("D2", "3")],
    "LED_B": [("U1", "7"), ("TP9", "1"), ("R5", "1")],
    "LED_BK": [("R5", "2"), ("D2", "4")],
}
NC = [("U1", p) for p in ("1", "4", "10", "11", "14")]

def build():
    blocks, pinmap = {}, {}
    for lid, (f, n) in STD.items():
        b = extract(f, n)
        b = b.replace(f'(symbol "{n}"', f'(symbol "{lid}"', 1)
        blocks[lid] = b; pinmap[lid] = pins_of(b)
    for lid, b in CUSTOM.items():
        blocks[lid] = b; pinmap[lid] = pins_of(b)
    # project library
    lib = ['(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "ventbox_gen")\n\t(generator_version "9.0")']
    for lid, b in CUSTOM.items():
        lib.append(b.replace(f'(symbol "{lid}"', f'(symbol "{lid.split(":")[1]}"', 1))
    lib.append(')')
    open(os.path.join(OUT, f"{PROJ}.kicad_sym"), "w").write("\n".join(lib) + "\n")
    open(os.path.join(OUT, "sym-lib-table"), "w").write(f'(sym_lib_table\n\t(version 7)\n\t(lib (name "{PROJ}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJ}.kicad_sym")(options "")(descr "Ventbox project symbols"))\n)\n')

    pos = {r: (x, y) for r, _, _, _, x, y, _, _ in PARTS}
    lidof = {r: l for r, l, *_ in PARTS}
    def pin_pt(ref, num):
        px, py, ang, _ = pinmap[lidof[ref]][num]
        X, Y = pos[ref]
        return round(X + px, 2), round(Y - py, 2), ang
    out = []
    def eff(j="", hide=False):
        return ('(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)' + (f'\n\t\t\t\t(justify {j})' if j else '')
                + ('\n\t\t\t\t(hide yes)' if hide else '') + '\n\t\t\t)')
    out.append(f'(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "{ROOT}")\n\t(paper "A4")')
    out.append('\t(title_block\n\t\t(title "Ventbox sub-board")\n\t\t(date "2026-11-08")\n\t\t(rev "1.2")\n\t\t(company "Group 2")\n'
               '\t\t(comment 1 "XIAO nRF52840 + SHT40 + Sunon UB5U3-700 + LiPo LP303035")\n\t\t(comment 2 "Sub-board 16x16 mm: Q1 R1-R5 D1 D2 SW1 TP1-TP9; U1 U2 BT1 M1 connected by soldered wires")\n\t\t(comment 3 "License: CERN-OHL-S-2.0")\n\t)')
    out.append('\t(lib_symbols\n' + "\n".join(blocks[l] for l in sorted(set(lidof.values()))) + '\n\t)')
    sym_uuid = {}
    for ref, lid, val, fp, x, y, onb, extra in PARTS:
        su = U(); sym_uuid[ref] = su
        vo = {"U1": (-13.97, 15.24), "U2": (-7.62, 10.16), "Q1": (5.08, 6.35), "M1": (5.08, 7.62)}.get(ref, (2.54, 6.35))
        ro = {"U1": (-2.54, -13.97), "U2": (-2.54, -8.89), "Q1": (5.08, -6.35), "M1": (5.08, -5.08)}.get(ref, (2.54, -6.35))
        props = [("Reference", ref, (x + ro[0], y + ro[1]), ""), ("Value", val, (x + vo[0], y + vo[1]), ""),
                 ("Footprint", fp, (x, y + 8.89), "hide"), ("Datasheet", "", (x, y + 8.89), "hide")]
        for k, v in extra.items(): props.append((k, v, (x, y + 8.89), "hide"))
        s = [f'\t(symbol\n\t\t(lib_id "{lid}")\n\t\t(at {x} {y} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom {"no" if ref.startswith("TP") else "yes"})\n\t\t(on_board {"yes" if onb else "no"})\n\t\t(dnp no)\n\t\t(uuid "{su}")']
        for k, v, (px, py), h in props:
            s.append(f'\t\t(property "{k}" "{v}"\n\t\t\t(at {px:.2f} {py:.2f} 0)\n\t\t\t' + eff("left" if k in ("Reference", "Value") else "", h == "hide") + '\n\t\t)')
        for num in pinmap[lid]:
            s.append(f'\t\t(pin "{num}"\n\t\t\t(uuid "{U()}")\n\t\t)')
        s.append(f'\t\t(instances\n\t\t\t(project "{PROJ}"\n\t\t\t\t(path "/{ROOT}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
        out.append("\n".join(s))
    # wires + labels
    for net, members in NETS.items():
        for ref, num in members:
            x, y, ang = pin_pt(ref, num)
            dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[int(ang)]
            x2, y2 = round(x + dx * 2.54, 2), round(y + dy * 2.54, 2)
            out.append(f'\t(wire\n\t\t(pts\n\t\t\t(xy {x} {y}) (xy {x2} {y2})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{U()}")\n\t)')
            la = {(-1, 0): 0, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)]
            just = "right bottom" if dx == -1 else "left bottom"
            if dy != 0: just = "left bottom"
            out.append(f'\t(label "{net}"\n\t\t(at {x2} {y2} {la if dy else 0})\n\t\t' + eff(just).replace("\t\t\t\t", "\t\t\t").replace("\t\t\t)", "\t\t)") + f'\n\t\t(uuid "{U()}")\n\t)')
    for ref, num in NC:
        x, y, _ = pin_pt(ref, num)
        out.append(f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{U()}")\n\t)')
    # notes
    notes = ["Sub-board 16x16 mm (on_board): Q1 AO3400A, R1 100R, R2 10k, D1 B5819W, SW1 TS-1187A, TP1..TP6 wire solder pads.",
             "U1 XIAO, U2 SHT40, BT1 battery, M1 fan: off-board parts, connected with 30 AWG silicone wire (on_board = no).",
             "Sunon UB5U3-700 fan runs on constant voltage (no PWM): firmware only switches FAN_PWM HIGH/LOW.",
             "D1 Schottky clamps the fan flyback pulse when Q1 turns off. R2 keeps Q1 off while the XIAO boots/sleeps.",
             "D2 common-anode RGB LED tied to VBAT; XIAO D7/D8/D6 pull LOW to light R/G/B (VBAT - 3.3 V < Vf: LED off when HIGH).",
             "Freshness timer: green 2 days -> orange (R + G PWM) 3 days -> red 2 days -> red double flash when expired."]
    for t, (x, y) in (("OFF-BOARD (wired): XIAO, battery, sensor", (20.32, 35.56)), ("FAN + FLYBACK DIODE", (165.1, 35.56)),
                      ("SUB-BOARD 16x16 mm: MOSFET switch", (165.1, 86.36)), ("SUB-BOARD: push button + 6 wire pads", (120.65, 119.38)),
                      ("SUB-BOARD: timer RGB LED + 3 pads", (114.3, 50.8))):
        out.append(f'\t(text "{t}"\n\t\t(exclude_from_sim no)\n\t\t(at {x} {y} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 2 2)\n\t\t\t\t(bold yes)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{U()}")\n\t)')
    for i, t in enumerate(notes):
        out.append(f'\t(text "{t}"\n\t\t(exclude_from_sim no)\n\t\t(at 20.32 {182.88 + i*3.81:.2f} 0)\n\t\t' + eff("left bottom").replace("\t\t\t\t", "\t\t\t").replace("\t\t\t)", "\t\t)") + f'\n\t\t(uuid "{U()}")\n\t)')
    out.append(f'\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)')
    open(os.path.join(OUT, f"{PROJ}.kicad_sch"), "w").write("\n".join(out) + "\n")
    json.dump({"root": ROOT, "symbols": sym_uuid, "parts": [(p[0], p[1], p[2], p[3], p[6], p[7]) for p in PARTS], "nets": NETS},
              open(os.path.join(OUT, "_sch_meta.json"), "w"), ensure_ascii=False, indent=1)
    pro = {"meta": {"filename": f"{PROJ}.kicad_pro", "version": 3},
           "board": {"design_settings": {"rules": {"min_clearance": 0.15, "min_track_width": 0.2, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.3}}},
           "net_settings": {"classes": [{"name": "Default", "clearance": 0.15, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3}], "meta": {"version": 4}},
           "schematic": {"meta": {"version": 1}}, "sheets": [[ROOT, "Root"]]}
    json.dump(pro, open(os.path.join(OUT, f"{PROJ}.kicad_pro"), "w"), indent=2)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); build(); print("sch ok")
