#!/usr/bin/env python3
"""
Stage 5 — "Sounds of Betelgeuse" (finale, SSTV edition)

The 116th picture, sent as Slow-Scan Television (Robot 36) — the way pictures
still travel over radio. NO programming needed to solve: any SSTV app decodes
it (Robot36 / Black Cat SSTV on a phone, QSSTV / MMSSTV on desktop). The mode
is auto-detected from the VIS header, so players don't even need its name.

Decoded, the image is the receiving dish in 2026 — the reply is a mirror of us.

Writes: betelgeuse_sstv.wav (player-facing, ~36s) + stage5_reference.png (key)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pysstv.color import Robot36

W, H = 320, 240
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def f(p, s): return ImageFont.truetype(p, s)
rng = np.random.default_rng(1977)

def make():
    img = Image.new("RGB", (W, H), (4, 4, 10)); d = ImageDraw.Draw(img)
    for _ in range(150):
        x, y = rng.integers(0, W), rng.integers(0, H)
        v = int(rng.integers(90, 255)); d.point((x, y), fill=(v, v, v))
    # thematic calibration ring (nod to the Record cover)
    d.ellipse([18, 150, 74, 206], outline=(120, 120, 140), width=1)
    # the dish that received the reply
    cx, cy = 205, 140
    d.arc([cx-92, cy-38, cx+92, cy+92], start=200, end=340, fill=(255,255,255), width=3)
    d.line([cx, cy+26, cx, cy-44], fill=(220,220,220), width=2)
    d.ellipse([cx-7, cy-52, cx+7, cy-38], outline=(230,230,230), width=2)
    d.line([cx-72, cy+58, cx, cy+92], fill=(150,150,160), width=2)
    d.line([cx+72, cy+58, cx, cy+92], fill=(150,150,160), width=2)
    d.line([cx, cy+92, cx, cy+108], fill=(150,150,160), width=3)
    # text
    d.text((44, 12), "SOUNDS OF BETELGEUSE", font=f(FB, 17), fill=(255,255,120))
    d.text((92, 198), "GOLDSTONE :: 2026", font=f(FB, 13), fill=(210,230,255))
    d.text((24, 218), "flag{we_are_the_signal_we_sent}", font=f(FM, 13), fill=(255,255,255))
    return img

def main():
    img = make(); img.save("stage5_reference.png")
    Robot36(img, 48000, 16).write_wav("betelgeuse_sstv.wav")
    print("wrote betelgeuse_sstv.wav (Robot36, ~36s) + stage5_reference.png")

if __name__ == "__main__":
    main()
