#!/usr/bin/env python3
"""
Stage 2 — "Sounds of Earth"
Alien re-synthesis of the Record's greeting, with Morse buried underneath.
Decoding the Morse yields the phrase that keys Stage 4.

Design goals:
  - Sounds unsettling / non-human (Shepard tones, detuned drones, sparse clicks).
  - Morse at 600 Hz sits ~ -18 dB under the bed so it's *hidden* to a casual ear...
  - ...but the bed is NOTCHED around 600 Hz so the Morse line pops on a spectrogram.
  - Everything lives 300 Hz - 6 kHz so it survives a speaker -> phone-mic path.

Outputs: alien_signal.wav
"""
import numpy as np
from scipy.io import wavfile
from scipy import signal as sig

FS = 44100
MORSE_HZ = 600.0
MORSE_TEXT = "AD ASTRA PER ASPERA"
DOT = 0.085                 # seconds; ~14 wpm, comfortable to read off a waterfall
DASH_STRETCH = 1.15         # dashes slightly too long -> "learned, not human"
rng = np.random.default_rng(1977)

# ---------------- Morse ----------------
MORSE = {
    'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.',
    'H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.',
    'O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-',
    'V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..'
}

def morse_envelope(text):
    """Return an on/off amplitude envelope (0/1) at FS for the given text."""
    unit = int(DOT * FS)
    on_dot  = np.ones(unit)
    on_dash = np.ones(int(unit * 3 * DASH_STRETCH))
    gap_sym = np.zeros(unit)          # between symbols in a letter
    gap_ltr = np.zeros(unit * 3)      # between letters
    gap_wrd = np.zeros(unit * 7)      # between words
    env = [np.zeros(int(0.5 * FS))]   # lead-in silence
    for word in text.split(' '):
        for li, letter in enumerate(word):
            if li: env.append(gap_ltr)
            for si, sym in enumerate(MORSE[letter]):
                if si: env.append(gap_sym)
                env.append(on_dash if sym == '-' else on_dot)
        env.append(gap_wrd)
    env.append(np.zeros(int(0.5 * FS)))
    return np.concatenate(env)

def make_morse(text, total_len):
    env = morse_envelope(text)
    # soft attack/decay so keying doesn't click (raised-cosine edges)
    edge = int(0.006 * FS)
    k = np.ones(edge * 2 + 1); k /= k.sum()
    env = np.convolve(env, k, mode='same')
    # loop/pad to fill the whole piece, offset so it isn't at t=0
    reps = int(np.ceil(total_len / len(env))) + 1
    env = np.tile(env, reps)[:total_len]
    t = np.arange(total_len) / FS
    tone = np.sin(2*np.pi*MORSE_HZ*t)
    # a touch of 2nd harmonic keeps it legible through a phone speaker
    tone += 0.15*np.sin(2*np.pi*2*MORSE_HZ*t)
    return tone * env

# ---------------- Dark, irradiated radio bed ----------------
def radio_hiss(total_len):
    """Interstation FM/SW hiss — broadband 'shhhh' that fades in and out."""
    n = rng.standard_normal(total_len)
    # shape to a radio-ish band and add slow fading between "stations"
    b,a = sig.butter(2, [350/(FS/2), 3000/(FS/2)], 'band')
    h = sig.lfilter(b,a,n)
    t = np.arange(total_len)/FS
    fade = 0.5 + 0.5*np.sin(2*np.pi*0.08*t + 0.7)
    fade *= 0.6 + 0.4*np.sin(2*np.pi*0.017*t)      # slower drift on top
    # occasional surges of louder hiss
    for _ in range(int(total_len/FS/5)):
        s = rng.integers(0,total_len); L = rng.integers(int(0.3*FS),int(1.2*FS))
        fade[s:s+L] *= rng.uniform(1.3,1.9)
    return (h*fade)/(np.max(np.abs(h*fade))+1e-9)

def brown_noise(total_len):
    """Brown (1/f^2) noise — heavy low end, dark hiss. The static floor."""
    w = rng.standard_normal(total_len)
    b = np.cumsum(w)                       # integrate -> brown
    b -= np.linspace(b[0], b[-1], total_len)   # kill DC drift
    return b/(np.max(np.abs(b))+1e-9)

def am_crackle(total_len, rate_hz=45):
    """Sparse pops/crackle like an AM set drowning in static & sferics."""
    out = np.zeros(total_len)
    n = rng.poisson(rate_hz*total_len/FS)
    idx = rng.integers(0, total_len, size=n)
    for i in idx:
        L = rng.integers(int(0.0008*FS), int(0.006*FS))
        env = np.exp(-np.linspace(0,9,L))
        pop = env*(rng.standard_normal(L))       # noisy pop, not tonal
        out[i:i+min(L, total_len-i)] += pop[:max(0,min(L,total_len-i))]*rng.uniform(0.4,1)
    return out/(np.max(np.abs(out))+1e-9)

def geiger(total_len):
    """Radiation counter — sharp clicks whose RATE surges and fades in bursts."""
    out = np.zeros(total_len)
    # slow random rate envelope: quiet, then a burst of activity, then quiet
    ctrl = np.interp(np.arange(total_len),
                     np.linspace(0,total_len, 60),
                     rng.random(60)**2)          # 0..1, spiky
    rate = 3 + 55*ctrl                            # clicks/sec, time-varying
    p = rate/FS
    fires = np.where(rng.random(total_len) < p)[0]
    for i in fires:
        L = rng.integers(int(0.0006*FS), int(0.0025*FS))
        env = np.exp(-np.linspace(0,10,L))
        out[i:i+min(L,total_len-i)] += (env*rng.standard_normal(L))[:max(0,min(L,total_len-i))]
    return out/(np.max(np.abs(out))+1e-9)

def heterodynes(total_len):
    """Drifting carrier whistles — the squeal of tuning a dying shortwave."""
    t = np.arange(total_len)/FS
    out = np.zeros(total_len)
    for _ in range(3):
        f0 = rng.uniform(950, 2200)                # kept away from 600 Hz Morse
        drift = f0 + 120*np.sin(2*np.pi*rng.uniform(0.01,0.04)*t + rng.uniform(0,6))
        drift += 40*rng.standard_normal(total_len).cumsum()/total_len*10
        gate = (0.5+0.5*np.sin(2*np.pi*rng.uniform(0.03,0.09)*t)).clip(0,1)**3
        out += gate*np.sin(2*np.pi*np.cumsum(drift)/FS)*rng.uniform(0.3,0.7)
    return out/(np.max(np.abs(out))+1e-9)

def dark_drone(total_len):
    """Low dissonant drone — minor-second & tritone beats for unease."""
    t = np.arange(total_len)/FS
    d = np.zeros(total_len)
    for f, a in [(41.2,1.0),(43.65,0.8),(58.27,0.5),(61.74,0.45),(87.31,0.25)]:
        breath = 0.6+0.4*np.sin(2*np.pi*(0.03+0.015*a)*t + a*5)
        d += a*breath*np.sin(2*np.pi*f*t)
    return d/(np.max(np.abs(d))+1e-9)

def dark_sweeps(total_len):
    """Occasional low descending noise surges — a wave of radiation passing."""
    out = np.zeros(total_len)
    for _ in range(max(1,int(total_len/FS/7))):
        start = rng.integers(0, max(1,total_len-int(3*FS)))
        L = rng.integers(int(1.5*FS), int(3.0*FS))
        n = rng.standard_normal(L)
        # descending band-pass sweep
        env = np.sin(np.pi*np.linspace(0,1,L))**2
        f_hi, f_lo = rng.uniform(1400,2000), rng.uniform(150,300)
        seg = np.zeros(L); step = L//8
        for k in range(8):
            fc = f_hi + (f_lo-f_hi)*k/7
            b,a = sig.butter(2, [max(60,fc-120)/(FS/2), (fc+120)/(FS/2)], 'band')
            s0,s1 = k*step, min(L,(k+1)*step)
            seg[s0:s1] = sig.lfilter(b,a,n)[s0:s1]
        out[start:start+L] += (seg*env)[:max(0,min(L,total_len-start))]
    return out/(np.max(np.abs(out))+1e-9)

def fade_gate(total_len):
    """Slow signal fade + hard dropouts, like a link on the edge of loss."""
    t = np.arange(total_len)/FS
    slow = 0.55+0.45*np.sin(2*np.pi*0.06*t + 1.3)
    # random dropouts
    g = np.ones(total_len)
    for _ in range(int(total_len/FS/4)):
        s = rng.integers(0,total_len); L = rng.integers(int(0.05*FS),int(0.25*FS))
        g[s:s+L] *= rng.uniform(0.1,0.4)
    g = sig.savgol_filter(g, int(0.02*FS)|1, 2)
    return slow*g

def grit(x, drive=2.6):
    """Waveshape + light bitcrush for a degraded, over-driven radio texture."""
    y = np.tanh(drive*x)/np.tanh(drive)
    step = 1/90.0                                  # ~ coarse quantization
    y = np.round(y/step)*step
    return y/(np.max(np.abs(y))+1e-9)

def convolve_reverb(x, decay=1.6):
    L = int(decay*FS)
    ir = rng.standard_normal(L)*np.exp(-np.linspace(0,7,L))
    ir[0] = 1.0
    y = sig.fftconvolve(x, ir)[:len(x)]
    return y/(np.max(np.abs(y))+1e-9)

def notch(x, f0=MORSE_HZ, Q=3.0):
    """Carve a dip around the Morse frequency so the code stands out visually."""
    b,a = sig.iirnotch(f0/(FS/2), Q)
    # apply twice for a deeper, wider trough
    return sig.lfilter(b,a, sig.lfilter(b,a,x))

# ---------------- Assemble ----------------
def main():
    dur = 30.0
    N = int(dur*FS)

    # layered irradiated-radio bed — heavy on static
    static  = 1.00*brown_noise(N) + 0.65*am_crackle(N) + 0.80*radio_hiss(N)
    bed = (0.95*static +
           0.55*geiger(N) +
           0.55*dark_drone(N) +
           0.30*heterodynes(N) +
           0.40*dark_sweeps(N))
    bed = convolve_reverb(bed, decay=2.2)
    bed *= fade_gate(N)                          # fading / dropouts
    bed = grit(bed, drive=2.8)                   # over-driven, degraded

    # DARK spectral tilt: roll off the highs, keep low-mid weight
    b,a = sig.butter(2, 300/(FS/2), 'high'); bed = sig.lfilter(b,a,bed)   # clear rumble
    b,a = sig.butter(4, 3200/(FS/2), 'low');  bed = sig.lfilter(b,a,bed)  # darken top
    # gentle low-shelf lift for weight
    b,a = sig.butter(2, 500/(FS/2), 'low'); bed = bed + 0.6*sig.lfilter(b,a,bed)

    # carve a real slot around 600 Hz so the code stays readable through grit
    bs = sig.butter(4, [520/(FS/2), 690/(FS/2)], 'bandstop')
    bed = sig.lfilter(*bs, bed)
    bed = sig.lfilter(*bs, bed)                   # twice -> deeper trough
    bed = bed/(np.max(np.abs(bed))+1e-9)

    morse = make_morse(MORSE_TEXT, N)

    # subtle sidechain: duck the bed a few dB where the Morse is keyed,
    # so radiation bursts can't bury a symbol (keeps the grit everywhere else)
    duck_env = np.abs(morse)
    duck_env = sig.savgol_filter(duck_env, int(0.03*FS)|1, 2)
    duck_env /= np.max(duck_env)+1e-9
    bed = bed * (1.0 - 0.4*duck_env)

    # morse buried under the gritty bed but sitting in the carved slot
    mix = 0.90*bed + 0.22*morse
    b,a = sig.butter(2, 140/(FS/2), 'high'); mix = sig.lfilter(b,a,mix)
    mix = mix/(np.max(np.abs(mix))+1e-9) * 0.9

    wavfile.write('alien_signal.wav', FS, (mix*32767).astype(np.int16))
    print(f"wrote alien_signal.wav  ({dur:.0f}s, {FS} Hz)")
    print(f"morse: '{MORSE_TEXT}'  @ {MORSE_HZ:.0f} Hz, dot={DOT*1000:.0f} ms")

if __name__ == '__main__':
    main()
