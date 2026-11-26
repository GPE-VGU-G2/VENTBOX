"""Fill the GND copper zone: /usr/bin/python3 fill_zones.py ventbox.kicad_pcb"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones())
pcbnew.SaveBoard(sys.argv[1], b); print("filled", [z.IsFilled() for z in b.Zones()])
