#!/usr/bin/env python3
"""
Stage 3 — "The Cover"
An image drawn in sound. View the spectrogram of cover_signal.wav and the
Golden Record cover appears — carrying the flag, the Stage-4 salt (as the
record's binary 'clock'), and a foreshadow of Stage-5's scan-line trick.

Pipeline:  build a high-contrast PNG  ->  additive-synthesise audio whose
spectrogram *is* that PNG  ->  (verify by re-rendering the spectrogram).
"""
import numpy as np
from scipy.io import wavfile
from PIL import Image, ImageDraw, ImageFont

FS       = 44100
F_LO     = 550       # bottom of the image band (Hz)
F_HI     = 4800      # top of the image band (Hz) — stays phone-mic friendly
COL_MS   = 20        # column hold -> ~18s total
IMG_W    = 900
IMG_H    = 300
rng = np.random.default_rng(1977)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SALT_DATE = "1977-09-05"          # Voyager 1 launch -> Stage 4 salt

def f(sz, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, sz)

def draw_cover():
    """White marks on black — the spectrogram will render white = energy."""
    img = Image.new("L", (IMG_W, IMG_H), 0)
    d = ImageDraw.Draw(img)

    # ---- left: the Record disc + a simple pulsar 'starburst' map ----
    cx, cy, r = 150, 180, 120
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=255, width=3)
    d.ellipse([cx-8, cy-8, cx+8, cy+8], outline=255, width=3)   # spindle hole
    for ang in np.linspace(0, 2*np.pi, 12, endpoint=False):
        # radial 'pulsar' rays of varying length (the map motif)
        L = r*rng.uniform(0.35, 0.98)
        x2 = cx + L*np.cos(ang); y2 = cy + L*np.sin(ang)
        d.line([cx, cy, x2, y2], fill=200, width=2)
        # binary tick-marks along a couple of rays (the 'period' code)
        if ang in (0.0,):
            pass

    # ---- right: the text panel ----
    x0 = 300
    d.text((x0, 24),  "SOUNDS OF EARTH", font=f(30, bold=True), fill=255)
    d.text((x0, 66),  "cover / side B", font=f(20), fill=180)

    # the flag (second visible line of the panel)
    d.text((x0, 120), "flag{a_present_from_a_small_distant_world}",
           font=f(19, bold=True), fill=255)

    # the Stage-4 salt, framed as the record's 'clock' reading
    d.text((x0, 168), "CLOCK / LAUNCH KEY:", font=f(18), fill=180)
    d.text((x0, 192), SALT_DATE, font=f(26, bold=True), fill=255)

    return img

def image_to_audio(img):
    """Additive synthesis: each image row -> a sine whose amplitude follows
    that row across time. Phase-continuous per row => no clicks."""
    arr = np.asarray(img).astype(np.float32) / 255.0     # (H, W), 0..1
    H, W = arr.shape
    col_samples = int(COL_MS/1000 * FS)
    total = W * col_samples
    t = np.arange(total) / FS

    # row index (top=0) -> frequency (top row = high freq)
    freqs = np.linspace(F_HI, F_LO, H)

    out = np.zeros(total, dtype=np.float32)
    for r in range(H):
        row = arr[r]
        if row.max() < 0.05:
            continue
        # amplitude envelope: hold each column value for col_samples
        env = np.repeat(row, col_samples)[:total]
        # smooth column edges a touch to avoid vertical ringing
        env = np.convolve(env, np.ones(64)/64, mode='same')
        phase = rng.uniform(0, 2*np.pi)
        out += env * np.sin(2*np.pi*freqs[r]*t + phase)

    out /= np.max(np.abs(out)) + 1e-9
    out *= 0.9
    return out, total/FS

def main():
    img = draw_cover()
    img.save("cover_reference.png")            # what the spectrogram should look like
    audio, dur = image_to_audio(img)
    wavfile.write("cover_signal.wav", FS, (audio*32767).astype(np.int16))
    print(f"wrote cover_reference.png  ({IMG_W}x{IMG_H})")
    print(f"wrote cover_signal.wav     ({dur:.1f}s, band {F_LO}-{F_HI} Hz)")
    print(f"salt: {SALT_DATE}")

if __name__ == "__main__":
    main()
