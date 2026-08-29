import numpy as np
from scipy.io import wavfile
from scipy import signal as sig
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def spec(fn, out, title):
    fs,x = wavfile.read(fn); x=x.astype(float)
    if x.ndim>1: x=x.mean(1)
    x/=np.max(np.abs(x))+1e-9
    f,t,S = sig.spectrogram(x, fs, nperseg=1024, noverlap=512, window='hann')
    S = 10*np.log10(S+1e-12)
    m = (f>=400)&(f<=5200); f=f[m]; S=S[m]
    plt.figure(figsize=(13,5))
    plt.imshow(S, origin='lower', aspect='auto', cmap='inferno',
               extent=[t[0],t[-1],f[0],f[-1]], vmin=-110, vmax=-45)
    plt.ylabel('Hz'); plt.xlabel('s'); plt.title(title)
    plt.tight_layout(); plt.savefig(out,dpi=100); plt.close(); print("wrote",out)

spec("cover_signal.wav","cover_spectrogram.png","cover_signal.wav — view as spectrogram")
fs,x = wavfile.read("cover_signal.wav"); x=x.astype(float); x/=np.max(np.abs(x))
b,a = sig.butter(4,[300/(fs/2),3600/(fs/2)],'band'); y=sig.lfilter(b,a,x)
y += 0.015*np.random.randn(len(y)); y=np.tanh(2.0*y)/2.0
wavfile.write("cover_mic.wav", fs, (y/np.max(np.abs(y))*0.9*32767).astype(np.int16))
spec("cover_mic.wav","cover_spectrogram_mic.png","after speaker->mic path")
