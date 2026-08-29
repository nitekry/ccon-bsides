# Challenge 3 — The Cover

- **Category:** Stego / spectrogram
- **Difficulty:** medium
- **Flag:** `flag{a_present_from_a_small_distant_world}`
- **Feeds forward:** salt **1977-09-05** (Voyager 1 launch) → confirmation stamp on Stage 4

## Description (CTFd)

> **The Cover**
> The reply came with a picture attached — but your speakers only cough up noise.
> The Record didn't *play* its images either; it *drew* them. Stop listening.
> Start looking. Somewhere in that screech is a face the machine wants you to see,
> and a number it wants you to keep.
>
> `Flag format: flag{...}`

## Delivery

`dist/cover_signal.wav` — 18 s that sounds like screeching noise. Its
**spectrogram is the Golden Record cover.** Hand it out as a file, or play it as a
second FM segment. Image energy lives 550–4800 Hz (phone-mic friendly).

## Player path

1. Realize the picture is *in the sound* (the trick the Record used for its 115
   images). Open a spectrogram viewer.
2. Read the cover: title, the **flag**, and **CLOCK / LAUNCH KEY: 1977-09-05**.
3. Keep the date — it's the Stage-4 salt.

### Viewing in Audacity
Track dropdown ▼ → **Spectrogram**. Then Spectrogram Settings: window size
**2048–4096**, scale **Linear**, min ~300 Hz, max ~5000 Hz, and drag the track
taller. (For decoding off a speaker, a live phone app like Spectroid/SpectrumView
is easier.)

## Files

**dist/**
- `cover_signal.wav` — the audio whose spectrogram is the cover

**src/**
- `gen_stage3.py` — draws the cover PNG and encodes it into audio
- `verify3.py` — renders the spectrogram back (proof) + a mic-path test
- `cover_reference.png` — the source image / answer key
- `cover_spectrogram.png` — the decoded spectrogram (proof it's readable)

## How it works

The generator draws a high-contrast PNG (disc + pulsar-map motif on the left, a
text panel on the right) and synthesizes audio by **additive synthesis**: each
image row becomes a sine whose amplitude follows that row across time
(phase-continuous per row → no clicks). Rows map to 550–4800 Hz, columns to time.
Viewing the spectrogram reproduces the image.

## Notes for the build team

- The panel ends at the date. Earlier drafts included Stage-5 scan-line hints
  here; those were **moved to the Stage-4 decrypted message** so this cover stays
  focused on the flag + salt.
- If you want the salt to be *harder* (encoded as pulsar-map binary instead of
  plain text), that's a one-function change in `gen_stage3.py` — ask.

## Build / regenerate

```
cd src && python3 gen_stage3.py     # writes ../dist/cover_signal.wav + reference PNGs
python3 verify3.py                   # re-renders cover_spectrogram.png to check readability
```

Requires: Python 3 + numpy + scipy + Pillow + matplotlib. Fonts: DejaVu
(`/usr/share/fonts/truetype/dejavu/`).
