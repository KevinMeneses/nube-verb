"""Compara los renders de tests/out con lo que dice la teoría. Sale con código 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, sys
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "signals"; SR = 48000
def a(db): return 10 ** (db / 20)
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
def load(name): x, sr = sf.read(D / f"{name}.wav"); assert sr == SR; return x
def src(name): return sf.read(S / f"{name}.wav")[0]
def rms(x): return db(np.sqrt(np.mean(np.asarray(x) ** 2)))
def band(x, lo, hi): return sg.sosfiltfilt(sg.butter(4, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)
def rt60(x, lo=500, hi=2000, t0=0.1, top=-5, bot=-25):
    """T20 × 3 por integración de Schroeder en una banda (los dos canales sumados en energía)"""
    y = band(x[int(t0 * SR):], lo, hi); e = (y ** 2).sum(1)
    edc = np.cumsum(e[::-1])[::-1]; edc = 10 * np.log10(edc / edc[0] + 1e-30)
    i1 = np.argmax(edc <= top); i2 = np.argmax(edc <= bot)
    t = np.arange(i1, i2) / SR; k = np.polyfit(t, edc[i1:i2], 1)[0]
    return -60 / k

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:34s} {got:+9.3f}   (esperado {want:+.3f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:34s} {got:+9.3f}   (entre {lo:+.3f} y {hi:+.3f})")

for p in sorted(q for q in D.glob("*.wav") if not q.stem.startswith("perf_")):
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 4:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +12 dBFS", np.abs(x).max())

# seco, mezcla y salida
x = load("mix0"); ref = src("sine1k")
scalar("mezcla 0 % = señal intacta (dB)", db(np.abs(x - ref).max()), -140, 20)
x = load("mix50")[int(0.05 * SR):int(0.45 * SR), 0]; r = ref[int(0.05 * SR):int(0.45 * SR), 0]
scalar("mezcla 50 %: seca × cos(45°)", db(np.abs(x - r * np.cos(np.pi / 4)).max()), -140, 20)
scalar("salida -6 dB", rms(load("out_m6")[:, 0]) - rms(ref[:, 0]), -6, 0.01)
x = load("envio"); i = int(0.1 * SR)
inrange("envío: sin señal seca (dB)", db(np.abs(x[i:i + int(0.049 * SR)]).max()), -300, -100)

# decay
for name, want in (("rt05", 0.5), ("rt2", 2), ("rt6", 6), ("rt2_eco", 2), ("rt2_mod", 2)):
    scalar(f"RT60 {name} (500-2k)", rt60(load(name)), want, want * 0.12)
x = load("rt2_low2"); g = rt60(x, 60, 150); print(f"    graves x2: RT 60-150 Hz {g:.2f} s, 500-2k {rt60(x):.2f} s")
inrange("graves × 2 (RT 60-150 Hz)", g, 3.2, 4.4)
x = load("rt2_high03"); g = rt60(x, 8000, 12000, bot=-20); print(f"    agudos x0.3: RT 8-12k {g:.2f} s, 500-1k {rt60(x, 300, 700):.2f} s")
inrange("agudos × 0.3 (RT 8-12 kHz)", g, 0.45, 0.85)
inrange("agudos × 0.3: medios quietos", rt60(x, 300, 700), 1.7, 2.3)

# pre-delay: primer eco
def onset(name):
    x = np.abs(load(name)).max(1); return (np.argmax(x > x.max() * 1e-3) - int(0.1 * SR)) / SR * 1000
# el primer eco llega despues del pre-delay + la difusion (~0.4 ms) + la modulacion de las lineas (hasta ~1 ms segun su fase)
inrange("pre-delay 100 ms (inicio, ms)", onset("pre100"), 100.0, 101.5)
inrange("pre-delay 1/8 a 120 BPM (ms)", onset("sync18"), 250.0, 251.5)

# ancho
x = load("width0"); inrange("ancho 0 %: L = R (dB)", db(np.abs(x[:, 0] - x[:, 1]).max()), -300, -110)
x = load("width100")[int(0.2 * SR):int(2 * SR)]; c = np.corrcoef(x[:, 0], x[:, 1])[0, 1]
inrange("ancho 100 %: correlación L/R", c, -0.3, 0.3)

# filtros
def bandlvl(name, lo, hi, t0=0.6, t1=2.4): return rms(band(load(name)[int(t0 * SR):int(t1 * SR)], lo, hi))
inrange("corte grave 500: -dB en 80-120", bandlvl("lc_off", 80, 120) - bandlvl("lc500", 80, 120), 20, 40)
inrange("corte grave 500: 3-5k intacto", bandlvl("lc_off", 3000, 5000) - bandlvl("lc500", 3000, 5000), -0.3, 0.3)
inrange("corte agudo 2k: -dB en 8-12k", bandlvl("lc_off", 8000, 12000) - bandlvl("hc2k", 8000, 12000), 20, 40)
inrange("época 70s: -dB en 10-14k", bandlvl("lc_off", 10000, 14000) - bandlvl("era70", 10000, 14000), 6, 60)
print(f"    nivel de la cola (ruido -12 dBFS RMS, Sala 2 s): {bandlvl('lc_off', 20, 20000, 1.5, 2.4) + 12:+.1f} dB respecto a la entrada")

# ducking
d0, d1 = bandlvl("duck_off", 20, 20000, 1.5, 2.4), bandlvl("duck12", 20, 20000, 1.5, 2.4)
scalar("ducking 12 dB durante la voz", d1 - d0, -12, 1.0)
d0, d1 = bandlvl("duck_off", 20, 20000, 3.2, 3.6), bandlvl("duck12", 20, 20000, 3.2, 3.6)
inrange("ducking: la cola vuelve después", d1 - d0, -2, 0.5)

# gate (ráfaga 0.5-1.0 s, hold 200 ms)
g0 = load("gate_off"); g1 = load("gate")
lv = lambda x, t0, t1: rms(x[int(t0 * SR):int(t1 * SR)])
inrange("gate: abierto durante el hold", lv(g1, 1.05, 1.15) - lv(g0, 1.05, 1.15), -1, 0.5)
inrange("gate: cerrado a 1.4 s (dB rel.)", lv(g1, 1.4, 1.6) - lv(g0, 1.4, 1.6), -300, -60)

# shimmer: energía en 880 Hz en la cola
def peak_at(name, f, t0=1.0, t1=2.0):
    x = load(name)[int(t0 * SR):int(t1 * SR), 0] * np.hanning(int((t1 - t0) * SR)); X = np.abs(np.fft.rfft(x)); fr = np.fft.rfftfreq(len(x), 1 / SR)
    return db(X[(fr > f - 15) & (fr < f + 15)].max())
h0 = peak_at("shim_off", 880) - peak_at("shim_off", 440); h1 = peak_at("shim60", 880) - peak_at("shim60", 440)
print(f"    shimmer: 880/440 sin {h0:.1f} dB, con 60 % {h1:.1f} dB")
inrange("shimmer +12 crea la octava (dB)", h1 - h0, 15, 80)
h1 = peak_at("shim_down", 220) - peak_at("shim_down", 440); h0 = peak_at("shim_off", 220) - peak_at("shim_off", 440)
inrange("shimmer -12 crea la octava abajo", h1 - h0, 15, 80)
x = load("shim_max"); late = rms(x[-2 * SR:]); mid = rms(x[4 * SR:6 * SR])
print(f"    shimmer al máximo (decay 20 s): pico {db(np.abs(x).max()):.1f} dBFS, 4-6 s {mid:.1f}, últimos 2 s {late:.1f}")
inrange("shimmer al máximo: no se dispara", db(np.abs(x).max()), -60, -6)
inrange("shimmer al máximo: la cola se apaga", late - mid, -80, -6)

# anti-eses
e = bandlvl("ess_off", 5000, 11000, 0.6, 1.5) - bandlvl("ess12", 5000, 11000, 0.6, 1.5)
inrange("anti-eses 12: baja las s (dB)", e, 8, 13)
v = bandlvl("vowel_off", 100, 4000, 0.6, 1.5) - bandlvl("vowel12", 100, 4000, 0.6, 1.5)
inrange("anti-eses 12: no toca la voz (dB)", v, -0.5, 0.5)

# freeze (activado en 1.5 s, el ruido sigue hasta 2.5 s pero ya no entra)
x = load("freeze"); a1, a2 = lv(x, 2.0, 2.5), lv(x, 5.0, 5.5)
print(f"    freeze: 2.0-2.5 s {a1:.1f} dB, 5.0-5.5 s {a2:.1f} dB")
inrange("freeze: la cola se sostiene", a2 - a1, -1.5, 0.5)

# espacios: mismo decay en todos
for m in range(6):
    inrange(f"espacio {m}: RT60 2 s", rt60(load(f"mode{m}")), 1.7, 2.35)
for name in ("tiny", "big_mod_max"):
    inrange(f"{name}: suena", rms(load(name)), -90, 0)
for p in range(1, 15):
    x = load(f"preset{p}"); inrange(f"preset {p}: cola audible tras la ráfaga", lv(x, 2.6, 2.8), -80, -10)
print("\nFALLAS:", fails)
sys.exit(1 if fails else 0)
