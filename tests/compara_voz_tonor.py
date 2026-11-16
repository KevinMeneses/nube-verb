"""Mide inicio, RT60 por octava, espectro con ruido y reparto con voz de los renders de tests/compara_voz_tonor.lua."""
import numpy as np, soundfile as sf, sys
from scipy import signal as sg
SR=48000; D="tests/out/cmp/"
def load(n): return sf.read(D+n+".wav")[0]
def band(x, lo, hi): return sg.sosfiltfilt(sg.butter(4, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)
def rt(x, lo, hi):
    y=band(x[int(0.1*SR):], lo, hi); e=(y**2).sum(1); edc=np.cumsum(e[::-1])[::-1]; edc=10*np.log10(edc/edc[0]+1e-30)
    i1=np.argmax(edc<=-5); i2=np.argmax(edc<=-25); t=np.arange(i1,i2)/SR; return -60/np.polyfit(t,edc[i1:i2],1)[0]
def db(v): return 10*np.log10(v+1e-30)
for w in ("orig","nube"):
    x=load(w+"_impulse"); env=np.abs(x).max(1)
    on=(np.argmax(env>env.max()*1e-2)-int(0.1*SR))/SR*1000
    rts=[rt(x,f/1.41,f*1.41) for f in (125,250,500,1000,2000,4000,8000)]
    n=load(w+"_noise_burst")[int(1.2*SR):int(2.4*SR)]
    bands=[db(np.mean(band(n,f/1.12,f*1.12)**2)) for f in (100,200,400,800,1600,3200,6400,10000)]
    v=load(w+"_vocal"); tot=db(np.mean(v**2)); c=np.corrcoef(v[:,0],v[:,1])[0,1]
    vb=[db(np.mean(band(v,f/1.41,f*1.41)**2))-tot for f in (125,250,500,1000,2000,4000,8000)]
    print(f"{w}: inicio {on:.1f} ms | RT 125..8k: "+" ".join(f"{r:.2f}" for r in rts))
    print(f"   ruido (dB, banda 1/6 oct) 100..10k: "+" ".join(f"{b:.1f}" for b in bands))
    print(f"   voz: nivel {tot:.1f} dB, corr L/R {c:.2f}, reparto por octava (rel.): "+" ".join(f"{b:.1f}" for b in vb))
