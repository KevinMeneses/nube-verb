"""Señales de prueba (48 kHz, float32)."""
import numpy as np, soundfile as sf, pathlib
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "signals"; D.mkdir(exist_ok=True)
SR = 48000
def a(db): return 10 ** (db / 20)
def save(name, *ch): sf.write(D / name, np.stack(ch, 1).astype(np.float32), SR, subtype="FLOAT")
rng = np.random.default_rng(7)
# impulso en 0.1 s, 14 s en total (para decays largos)
imp = np.zeros(SR * 14); imp[int(0.1 * SR)] = 0.5; save("impulse.wav", imp, imp)
# ruido rosado -12 dBFS RMS de 0.5 a 2.5 s, luego silencio hasta 6 s
def pink(n):
    w = rng.standard_normal(n); b, aa = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    p = sg.lfilter(b, aa, w); return p / np.sqrt(np.mean(p ** 2))
n = SR * 6; nz = np.zeros(n); i0, i1 = int(0.5 * SR), int(2.5 * SR); nz[i0:i1] = a(-12) * pink(i1 - i0)
nz[i0:i0 + 480] *= np.linspace(0, 1, 480); nz[i1 - 480:i1] *= np.linspace(1, 0, 480)
save("noise_burst.wav", nz, nz)
# rafaga corta (0.5-1.0 s) para el gate
nb = np.zeros(n); i0, i1 = int(0.5 * SR), int(1.0 * SR); nb[i0:i1] = a(-12) * pink(i1 - i0); save("short_burst.wav", nb, nb)
# seno 1 kHz -6 dBFS 3 s (pasar seco / mezcla)
t = np.arange(SR * 3) / SR; s = a(-6) * np.sin(2 * np.pi * 1000 * t); save("sine1k.wav", s, s)
# seno 440 Hz 0.5 s y silencio (shimmer)
t = np.arange(SR * 6) / SR; s4 = np.where(t < 0.6, a(-12) * np.sin(2 * np.pi * 440 * t), 0); s4[int(0.55 * SR):int(0.6 * SR)] *= np.linspace(1, 0, int(0.05 * SR)); save("sine440_burst.wav", s4, s4)
# "s": ruido 6-10 kHz (0.5-1.5 s); "vocal": tono de 200 Hz con armónicos que caen (0.5-1.5 s)
hb = sg.sosfilt(sg.butter(6, [6000, 10000], "band", fs=SR, output="sos"), rng.standard_normal(SR * 4)); hb /= np.sqrt(np.mean(hb ** 2))
ss = np.zeros(SR * 4); ss[SR // 2:SR * 3 // 2] = a(-15) * hb[SR // 2:SR * 3 // 2]; save("ess.wav", ss, ss)
t = np.arange(SR * 4) / SR; vo = sum(a(-6 * k) * np.sin(2 * np.pi * 200 * (k + 1) * t) for k in range(10)); vo = np.where((t > 0.5) & (t < 1.5), vo, 0) * a(-12)
save("vowel.wav", vo, vo)
print("ok", sorted(p.name for p in D.iterdir()))
# voz seca de Nube baja (14 s + 3 s de silencio) para la comparación con Voz Tonor y las demos
V = pathlib.Path.home() / "Music/ClaudeBeats/Media/voz_sola_seca.wav"
if V.exists():
    v, vsr = sf.read(V); assert vsr == SR
    sf.write(D / "vocal.wav", np.concatenate([v[:14 * SR], np.zeros((3 * SR, v.shape[1]))]).astype(np.float32), SR, subtype="FLOAT")
    print("ok vocal.wav")
