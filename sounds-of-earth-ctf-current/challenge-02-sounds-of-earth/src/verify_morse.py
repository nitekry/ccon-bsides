#!/usr/bin/env python3
"""Recover the Morse from alien_signal.wav to prove it survives the mix."""
import sys, numpy as np
from scipy.io import wavfile
from scipy import signal as sig

FS_HZ = 600.0
IN = sys.argv[1] if len(sys.argv) > 1 else 'alien_signal.wav'

INV = {'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G',
 '....':'H','..':'I','.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O',
 '.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W',
 '-..-':'X','-.--':'Y','--..':'Z'}

fs, x = wavfile.read(IN)
if x.ndim > 1: x = x.mean(1)
x = x.astype(float); x /= np.max(np.abs(x))+1e-9

# bandpass around 600 Hz, then amplitude envelope
b,a = sig.butter(4, [(FS_HZ-60)/(fs/2),(FS_HZ+60)/(fs/2)], 'band')
y = sig.lfilter(b,a,x)
env = np.abs(sig.hilbert(y))
# smooth
env = sig.savgol_filter(env, int(0.01*fs)|1, 2)
env /= np.max(env)+1e-9

# adaptive threshold
thr = np.mean(env) + 0.5*np.std(env)
on = env > thr

# find on-runs and off-runs
def runs(mask):
    out=[]; i=0; n=len(mask)
    while i<n:
        j=i
        while j<n and mask[j]==mask[i]: j+=1
        out.append((mask[i], (j-i)/fs)); i=j
    return out

r = runs(on)
on_durs = sorted(d for v,d in r if v)
if not on_durs:
    print("no keying detected"); sys.exit(1)
# dot length ~ shortest cluster of on-durations
dot = np.median([d for d in on_durs if d < np.median(on_durs)*1.8]) or on_durs[0]

text=""; cur=""
for v,d in r:
    u = d/dot
    if v:                       # ON: dot or dash
        cur += '.' if u < 2.0 else '-'
    else:                       # OFF: symbol / letter / word gap
        if u < 2.0:
            pass                # intra-letter
        elif u < 5.0:
            text += INV.get(cur,'?'); cur=""
        else:
            if cur: text += INV.get(cur,'?')
            text += ' '; cur=""
if cur: text += INV.get(cur,'?')

# collapse repeats (message loops) -> show one clean copy
words = [w for w in text.split(' ') if w]
print("decoded stream :", text.strip())
# try to find the 3-word phrase
for i in range(len(words)-2):
    tri = ' '.join(words[i:i+3])
    if tri.startswith('AD') and 'ASTRA' in words[i:i+3][1:]+[words[i+1]]:
        pass
print("first 3 words  :", ' '.join(words[:3]) if len(words)>=3 else words)
print("dot estimate   : %.0f ms" % (dot*1000))
