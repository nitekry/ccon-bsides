# Challenge 5 — Sounds of Betelgeuse  (finale)

- **Category:** Radio / image (SSTV)
- **Difficulty:** medium (recognition + run-a-tool)
- **Flag:** `flag{we_are_the_signal_we_sent}`
- **Pointed to by:** Stage 4's decrypted line — *"…SLOW-SCANNED IT BACK TO YOU. LET YOUR RADIO DRAW THE LINES."*

## Description (CTFd)

> **Sounds of Betelgeuse**
> The reply kept one last thing: the 116th picture. It didn't send a file — it
> *drew* it, line by line, the way we still send pictures over the air. Let your
> radio paint it and see what answered us.
>
> `Flag format: flag{...}`

## The reveal

Decoded, the image is the **receiving dish, timestamped 2026** — the punchline of
the whole CTF. The "alien" reply is a mirror: *we are the signal we sent.* The
flag sits at the bottom of the picture.

## Delivery

`dist/betelgeuse_sstv.wav` — a real **Robot 36 SSTV** transmission (~36 s). Deliver
as a file linked from Stage 4, or play it on air / into the station speaker.

## Player path — NO programming

1. Realize the screech is a picture again — but this time it's **SSTV** (slow-scan
   TV), not a spectrogram.
2. Decode with any SSTV app — **no code required**:
   - Phone: **Robot36** (Android) or **Black Cat SSTV** (iOS) — point it at the speaker.
   - Desktop: **QSSTV** / **MMSSTV** — feed the WAV.
3. The mode auto-detects from the VIS header, so players don't need to know it's
   Robot 36 or any timing. The image draws itself -> read the flag.

> Author note: SSTV apps only. This is **not** a spectrogram (that was Stage 3) and
> **not** a raw scan-line file needing a script. A one-line CTFd hint steering
> stuck players to "an SSTV decoder app" is recommended.

## Files

**dist/**
- `betelgeuse_sstv.wav` — the Robot 36 transmission

**src/**
- `gen_stage5_sstv.py` — draws the image and encodes it (pysstv, Robot36)
- `stage5_reference.png` — the source image (answer key)
- `stage5_sstv_decoded.png` — proof: decoded back from the WAV

## How it works

The generator draws a 320x240 image (dish + starfield + title + flag) and encodes
it with **pysstv** in Robot 36. It's a standard, VIS-tagged SSTV signal, so every
mainstream SSTV decoder handles it. Verified here by decoding the WAV back with the
`colaclanth/sstv` decoder (auto-detects "Robot 36", image reconstructs, flag legible).

## Build / regenerate

```
cd src && python3 gen_stage5_sstv.py     # writes ../dist/betelgeuse_sstv.wav + reference PNG
```
Requires: Python 3 + numpy + Pillow + `pysstv` (`pip install pysstv`).
Verify with any SSTV decoder (a phone app, or the `colaclanth/sstv` CLI).

## Difficulty options (for the team)

- **Easier:** add the CTFd hint naming "SSTV decoder app".
- **Harder alternate:** we also prototyped a **raw scan-line** version (the exact
  Golden Record method - the waveform level *is* the brightness, decoded by writing
  a reshape script, "a circle proves your timing"). That's a programming/forensics
  finale. Ask if you want it swapped in or offered as a bonus.
