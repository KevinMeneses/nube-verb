"""Ayudante para probar la interfaz con cliclick (ventana del FX en su posición/tamaño por defecto)."""
import subprocess, time, pathlib, re
WX, WY = 26, 66 + 53            # esquina del área gráfica del FX (puntos), bajo la cabecera de REAPER
ROOT = pathlib.Path(__file__).resolve().parent.parent
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "60", *args], check=True); time.sleep(0.4)
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path): subprocess.run(["screencapture", "-x", "-R26,66,1000,693", path], check=True); return path
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True)
    subprocess.Popen(["/Applications/REAPER.app/Contents/MacOS/REAPER", "-nonewinst", str(ROOT / "tests/ui_dump.lua")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    """valor formateado del slider n (1..30)"""
    m = re.search(rf"^{n} .*? = (.*)$", dump(), re.M); return m.group(1) if m else None
def drag(x0, y0, x1, y1, steps=8):
    cc(f"dd:{pt(x0, y0)}")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
# layout (ventana 1000x640): py = 378, área de gráficas y = 54..368
PY = 378
MODE = lambda k: (14 + 58 + k * 84 + 40, PY + 20)
KNOB = lambda i: (56 + i * 86, PY + 92)
SMALL = lambda i: (176 + i * 72, PY + 190)
TAB = lambda k: (70, PY + 161 + k * 26)
FREEZE = (1000 - 14 - 55, PY + 20)
SYNC = (1000 - 14 - 110 - 140 + 66, PY + 20)
