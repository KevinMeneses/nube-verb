"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh) y la ventana del FX al frente."""
import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ui import *
OUT = "/private/tmp/claude-501/-Users-kevinmeneses/a0c57d58-1422-40f8-b1a6-7da020557c1d/scratchpad"
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:42s} {got!r}")
def num(s): return float(s.split()[0]) if s else float("nan")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
cc(f"c:{pt(500, 5)}")                                     # foco en la ventana del FX
check("arranca con preset 3 (Sala)", param(1), "Sala")
cc(f"c:{pt(*MODE(0))}"); check("clic en Placa", param(1), "Placa")
cc(f"c:{pt(*MODE(5))}"); check("clic en Nube", param(1), "Nube")
d0 = num(param(5)); x, y = KNOB(2); drag(x, y, x, y - 60)
check("arrastrar Decay hacia arriba sube", num(param(5)), lambda v: v > d0 * 1.3)
cc(f"dc:{pt(x, y)}"); check("doble clic en Decay = 2 s", num(param(5)), 2.0)
x, y = KNOB(0); cc(f"m:{pt(x, y)}"); m0 = num(param(2)); wheel(5)
check("rueda sobre Mezcla sube", num(param(2)), lambda v: v > m0 + 1)
cc(f"c:{pt(*TAB(1))}"); x, y = SMALL(0); drag(x, y, x, y - 70)
check("pestaña Dinámica: arrastrar Ducking", num(param(19)), lambda v: v > 3)
cc(f"c:{pt(*TAB(2))}"); x, y = SMALL(2 if False else 2); x += 20; drag(x, y, x, y - 60)
check("pestaña Movimiento: Shimmer sube", num(param(24)), lambda v: v > 10)
cc(f"c:{pt(*FREEZE)}"); check("Freeze encendido", param(27), "Encendido")
shot(f"{OUT}/ui_freeze.png")
cc(f"c:{pt(*FREEZE)}"); check("Freeze apagado", param(27), "Apagado")
cc(f"c:{pt(*SYNC)}"); check("Pre-delay a tempo = 1/16", param(4), "1/16")
cc(f"c:{pt(*SYNC)}"); check("Pre-delay a tempo apagado", param(4), "Apagado")
# curva de decay: punto de medios (en x = sqrt(cruce grave * cruce agudo)) hacia arriba
import math
dx0, dw = 1000 - 14 - 96 - 16 - 341.88, 341.88   # dw = min(dh*1.25, (1000-96-90)*0.42) con dh = 314
f2x = lambda f: dx0 + dw * math.log(f / 20) / math.log(1000)
r2y = lambda r: 54 + 20 + (314 - 38) * (1 - math.log(r / 0.1) / math.log(300))
fl, fh = num(param(13)), float(param(15).split()[0]) * (1000 if "k" in param(15) else 1)
xm, ym = f2x(math.sqrt(fl * fh)), r2y(2.0)
drag(xm, ym, xm, ym - 40); check("punto medios arriba = más decay", num(param(5)), lambda v: v > 3)
xh, yh = f2x(fh), r2y(num(param(5)) * num(param(14).replace("x", "")))
drag(xh, yh, xh - 40, yh + 30); check("punto agudos: cruce agudo baja", param(15), lambda v: num(v) < fh * 0.9)
check("punto agudos: agudos x baja", num(param(14)), lambda v: v < 0.6)
# vista en vivo
cc(f"c:{pt(40 + (1000 - 14 - 96 - 16 - 341.88 - 16 - 40) - 8 - 128 + 31 + 66, 54 + 11)}"); time.sleep(1.5)
shot(f"{OUT}/ui_envivo.png")
# presets por el menú
cc(f"c:{pt(190, 22)}"); time.sleep(0.6); cc("kp:arrow-down", "kp:return")
check("menú Presets → Voz rap - placa corta", (param(1), param(2)), ("Placa", "15.0"))
print("FALLAS:", fails)
