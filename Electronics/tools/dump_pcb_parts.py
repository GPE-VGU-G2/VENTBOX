"""Export sub-board component positions/sizes to JSON for the CadQuery model."""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); out = []
for f in b.GetFootprints():
    p = f.GetPosition()
    out.append({"ref": f.GetReference(), "fp": str(f.GetFPID().GetLibItemName()), "x": pcbnew.ToMM(p.x) - 100, "y": pcbnew.ToMM(p.y) - 100,
                "rot": f.GetOrientationDegrees(),
                "pads": [[pcbnew.ToMM(q.GetPosition().x) - 100, pcbnew.ToMM(q.GetPosition().y) - 100,
                          pcbnew.ToMM(q.GetBoundingBox().GetWidth()), pcbnew.ToMM(q.GetBoundingBox().GetHeight())] for q in f.Pads()]})
json.dump({"board": [16.0, 16.0, 0.8], "parts": out}, open(sys.argv[2], "w"), indent=1); print(len(out))
