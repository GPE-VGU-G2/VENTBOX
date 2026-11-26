"""Generate the 16x16 mm sub-board PCB (KiCad 9) from _sch_meta.json, routed with Freerouting.
Run with KiCad's python:  /usr/bin/python3 gen_pcb.py <project_dir> [freerouting.jar]
"""
import sys, os, json, subprocess
import pcbnew
from pcbnew import VECTOR2I, FromMM as M

D = sys.argv[1]; JAR = sys.argv[2] if len(sys.argv) > 2 else None
meta = json.load(open(os.path.join(D, "_sch_meta.json")))
FPL = "/usr/share/kicad/footprints/"
IO = pcbnew.PCB_IO_KICAD_SEXPR()
OX, OY, W, H = 100.0, 100.0, 16.0, 16.0
# position (mm, origin at the board's top-left corner), rotation (degrees)
PLACE = {"SW1": (6.5, 5.5, 0), "R1": (4.0, 1.6, 0), "R2": (12.6, 2.4, 90), "Q1": (13.5, 5.6, 0), "D1": (13.6, 9.9, 90),
         "TP1": (1.75, 13.6, 0), "TP2": (4.25, 13.6, 0), "TP3": (6.75, 13.6, 0), "TP4": (9.25, 13.6, 0), "TP5": (11.75, 13.6, 0), "TP6": (14.25, 13.6, 0),
         # rev 1.1: timer RGB LED (D2 centre aligned with the light pipe in the module cover) + 3 resistors + 3 pads
         "D2": (11.2, 10.0, 0), "R3": (7.6, 8.9, 0), "R4": (7.6, 10.0, 0), "R5": (7.6, 11.1, 0),
         "TP7": (1.6, 10.6, 0), "TP8": (3.6, 10.6, 0), "TP9": (5.6, 10.6, 0)}

b = pcbnew.BOARD()
b.SetFileName(os.path.join(D, "ventbox.kicad_pcb"))
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("Ventbox sub-board"); tb.SetDate("2026-11-08"); tb.SetRevision("1.2")
tb.SetCompany("Group 2"); tb.SetComment(0, "Sub-board 16x16 mm, 2 layers, FR-4 0.8 mm"); tb.SetComment(1, "License: CERN-OHL-S-2.0")
b.SetTitleBlock(tb)
ds = b.GetDesignSettings()
ds.SetBoardThickness(M(0.8))
ds.m_MinClearance = M(0.15); ds.m_TrackMinWidth = M(0.2); ds.m_ViasMinSize = M(0.5); ds.m_MinThroughDrill = M(0.3)
ds.m_CopperEdgeClearance = M(0.3)
nc = ds.m_NetSettings.GetDefaultNetclass()
nc.SetClearance(M(0.15)); nc.SetTrackWidth(M(0.3)); nc.SetViaDiameter(M(0.6)); nc.SetViaDrill(M(0.3))
b.SetCopperLayerCount(2)

nets = {}
for n in meta["nets"]:
    ni = pcbnew.NETINFO_ITEM(b, "/" + n); b.Add(ni); nets[n] = ni
pinnet = {}
for n, mem in meta["nets"].items():
    for r, p in mem: pinnet[(r, p)] = n

for ref, lid, val, fp, onb, extra in meta["parts"]:
    if not onb: continue
    lib, name = fp.split(":")
    f = IO.FootprintLoad((os.path.join(D, lib) if lib == "ventbox" else FPL + lib) + ".pretty", name)
    f.SetReference(ref); f.SetValue(val)
    f.Reference().SetVisible(False); f.Value().SetVisible(False)   # board too small: reference designators are shown on F.Fab
    f.SetFPIDAsString(fp)
    f.SetPath(pcbnew.KIID_PATH("/" + meta["symbols"][ref]))
    f.SetSheetname("/"); f.SetSheetfile("ventbox.kicad_sch")
    for k, v in extra.items():
        f.SetField(k, v)
    for fld in f.GetFields():
        fld.SetLayer(pcbnew.F_Fab); fld.SetVisible(fld.GetName() == "Reference")
        fld.SetTextSize(VECTOR2I(M(0.5), M(0.5))); fld.SetTextThickness(M(0.08))
    x, y, a = PLACE[ref]
    b.Add(f)
    f.SetPosition(VECTOR2I(M(OX + x), M(OY + y)))
    if a: f.SetOrientationDegrees(a)
    for pad in f.Pads():
        n = pinnet.get((ref, pad.GetNumber()))
        if n: pad.SetNet(nets[n])
    for it in f.GraphicalItems():          # 16x16 board: move footprint silkscreen graphics to the Fab layer, keep only custom text
        if it.GetLayer() == pcbnew.F_SilkS: it.SetLayer(pcbnew.F_Fab)

# board outline with 1 mm corner radius
def seg(x0, y0, x1, y1):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(M(0.1))
    s.SetStart(VECTOR2I(M(x0), M(y0))); s.SetEnd(VECTOR2I(M(x1), M(y1))); b.Add(s)
def arc(cx, cy, sx, sy, ang):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(M(0.1))
    s.SetCenter(VECTOR2I(M(cx), M(cy))); s.SetStart(VECTOR2I(M(sx), M(sy))); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T)); b.Add(s)
r = 1.0; x0, y0, x1, y1 = OX, OY, OX + W, OY + H
seg(x0 + r, y0, x1 - r, y0); seg(x1, y0 + r, x1, y1 - r); seg(x1 - r, y1, x0 + r, y1); seg(x0, y1 - r, x0, y0 + r)
arc(x1 - r, y0 + r, x1 - r, y0, 90); arc(x1 - r, y1 - r, x1, y1 - r, 90); arc(x0 + r, y1 - r, x0 + r, y1, 90); arc(x0 + r, y0 + r, x0, y0 + r, 90)

# silkscreen text
def txt(s, x, y, layer=pcbnew.F_SilkS, size=0.7):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetPosition(VECTOR2I(M(x), M(y)))
    t.SetTextSize(VECTOR2I(M(size), M(size))); t.SetTextThickness(M(0.12))
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    b.Add(t)
for i, lab in enumerate(["BT", "PW", "G", "B+", "F+", "F-"]):
    txt(lab, OX + 1.75 + i * 2.5, OY + 13.6, pcbnew.B_SilkS, 0.8)   # pad labels printed on the back, directly behind each pad
txt("K", OX + 12.2, OY + 11.55, size=0.8)                    # cathode (bar) of D1
for i, lab in enumerate(["R", "G", "B"]):
    txt(lab, OX + 1.6 + i * 2.0, OY + 10.6, pcbnew.B_SilkS, 0.8)       # labels of the 3 LED pads on the back
txt("VENTBOX v1.2", OX + 8, OY + 4.5, pcbnew.B_SilkS, 1.0)
txt("CERN-OHL-S", OX + 8, OY + 7.0, pcbnew.B_SilkS, 0.8)
txt("2026-11", OX + 8, OY + 9.3, pcbnew.B_SilkS, 0.8)

pcb = os.path.join(D, "ventbox.kicad_pcb")
pcbnew.SaveBoard(pcb, b)

if JAR:
    dsn = os.path.join(D, "_route.dsn"); ses = os.path.join(D, "_route.ses")
    assert pcbnew.ExportSpecctraDSN(b, dsn)
    subprocess.run(["java", "-jar", JAR, "-de", dsn, "-do", ses, "-mp", "30", "--gui.enabled=false"], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    assert os.path.exists(ses), "freerouting failed"
    pcbnew.ImportSpecctraSES(b, ses)
    os.remove(dsn); os.remove(ses)

# GND zone (top layer)
for layer in (pcbnew.F_Cu,):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(nets["GND"])
    z.SetLocalClearance(M(0.2)); z.SetMinThickness(M(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); z.SetThermalReliefGap(M(0.2)); z.SetThermalReliefSpokeWidth(M(0.3))
    ol = z.Outline(); ol.NewOutline()
    for (px, py) in ((x0 + 0.2, y0 + 0.2), (x1 - 0.2, y0 + 0.2), (x1 - 0.2, y1 - 0.2), (x0 + 0.2, y1 - 0.2)):
        ol.Append(M(px), M(py))
    b.Add(z)
# the copper zone is filled with: kicad-cli pcb drc --refill-zones --save-board
pcbnew.SaveBoard(pcb, b)
print("pcb ok", len(b.GetTracks()), "tracks/vias")
